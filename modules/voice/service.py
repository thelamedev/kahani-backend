import aiohttp
import base64
import os
import secrets
import asyncio

from shared.ffmpeg import merge_audio_files_async
from shared.language_codes import LANGUAGE_CODES
from shared.llm.sarvam_tts import VoiceConfig, generate_sarvam_voice
from shared.utils import delete_files_by_pattern

NUM_VOICE_WORKERS = 4


async def voice_worker(
    in_queue: asyncio.Queue,
    out_queue: asyncio.Queue,
    read_lock: asyncio.Lock,
    write_lock: asyncio.Lock,
    session: aiohttp.ClientSession,
):
    while True:
        try:
            async with read_lock:
                item = in_queue.get_nowait()

            req_id = item["request_id"]
            item_file_path = f"/tmp/kahani/{req_id}__{item['index']:03}.wav"

            # generate the voice for this item and save it somewhere for merger
            audio_response = await generate_sarvam_voice(
                item["text"],
                LANGUAGE_CODES[item["language"]],
                VoiceConfig(**item["voice_config"]),
                session,
            )

            item["voice_sample_path"] = ""
            audio_buffer_encoded = audio_response.get("audios", [None])[0]

            if audio_buffer_encoded:
                audio_buffer = base64.b64decode(audio_buffer_encoded)
                with open(item_file_path, "wb") as fp:
                    fp.write(audio_buffer)

                item["voice_sample_path"] = item_file_path

            async with write_lock:
                await out_queue.put(item)
        except (asyncio.QueueEmpty, asyncio.QueueShutDown):
            break
        except Exception as e:
            print(e)


async def generate_voice_for_script(script: list[dict], language: str):
    """
    Generate a combines voice set for a script and merge the speaker audio into a single audio sample
    using something like pydub of ffmpeg.
    """

    req_id = secrets.token_hex(8)
    read_lock = asyncio.Lock()
    write_lock = asyncio.Lock()

    script_with_ids = []
    for idx, item in enumerate(script):
        item_with_args = {
            **item,
            "index": idx,
            "request_id": req_id,
            "language": language,
        }
        vm = item_with_args["voice_config"].pop("voice_model")
        item_with_args["voice_config"]["speaker"] = vm
        item_with_args["voice_config"]["pace"] = 1
        script_with_ids.append(item_with_args)

    script_queue = asyncio.Queue()
    for item in script_with_ids:
        await script_queue.put(item)

    results_queue = asyncio.Queue()

    # Ensure that the result directory is available
    os.makedirs("/tmp/kahani/compiled", exist_ok=True)

    worker_tasks = []
    async with aiohttp.ClientSession() as session:
        for _ in range(NUM_VOICE_WORKERS):
            t = asyncio.create_task(
                voice_worker(
                    script_queue,
                    results_queue,
                    read_lock,
                    write_lock,
                    session,
                )
            )
            worker_tasks.append(t)

        await asyncio.wait(worker_tasks)

    output_list = []
    while not results_queue.empty():
        try:
            output_list.append(await results_queue.get())
        except (asyncio.QueueEmpty, asyncio.QueueShutDown) as e:
            print(e)
            continue

    # sorting the list in order of original speech in script
    output_list.sort(key=lambda x: x["index"])

    # merge all the items in the output list using ffmpeg
    file_paths = [item["voice_sample_path"] for item in output_list]

    if not file_paths:
        raise Exception("failed to generate audio")

    output_file_path = await merge_audio_files_async(
        file_paths,
        f"/tmp/kahani/compiled/{req_id}_compiled.wav",
    )
    delete_files_by_pattern(
        "/tmp/kahani/",
        f"{req_id}_*.wav",
        dry_run=True,
    )

    return output_file_path
