import asyncio
from shared.ffmpeg import merge_audio_files_async


async def test_merge():
    await merge_audio_files_async(
        ["sample1.wav", "sample2.wav", "sample3.wav"],
        "./tmp/sample.wav",
    )


if __name__ == "__main__":
    asyncio.run(test_merge())
