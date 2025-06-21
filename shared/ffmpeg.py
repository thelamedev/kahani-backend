import asyncio
import subprocess
import os
import tempfile
import aiofiles

from shared.utils import find_ffmpeg


async def merge_audio_files_async(file_paths, output_path):
    """
    Asynchronously merges multiple audio files into a single file using ffmpeg.

    This non-blocking function uses ffmpeg's 'concat' demuxer, which is fast and
    avoids re-encoding. It is suitable for use in async applications (e.g., web servers)
    where you don't want to block the event loop.

    Args:
        file_paths (list): A list of strings, where each string is the path
                           to an audio file to be merged.
        output_path (str): The path for the final merged audio file.

    Returns:
        str: The path to the successfully created merged file (the output_path).

    Raises:
        ValueError: If the file_paths list is empty.
        FileNotFoundError: If ffmpeg is not installed or if any input files do not exist.
        subprocess.CalledProcessError: If ffmpeg returns a non-zero exit code.
    """
    if not isinstance(file_paths, list) or not file_paths:
        raise ValueError("Input 'file_paths' must be a non-empty list.")

    # Pre-flight checks (these are quick, so no need to be async)
    ffmpeg_executable = find_ffmpeg()
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Input file not found: {path}")

    # Handle the edge case of a single file asynchronously
    if len(file_paths) == 1:
        print("Only one file provided. Asynchronously copying it to the output path.")
        async with aiofiles.open(file_paths[0], "rb") as src:
            async with aiofiles.open(output_path, "wb") as dst:
                await dst.write(await src.read())
        return output_path

    # We need a temporary file to list the inputs for ffmpeg's concat demuxer.
    # The temp file path is created synchronously, but written to asynchronously.
    temp_dir = tempfile.gettempdir()
    list_file_path = os.path.join(temp_dir, f"ffmpeg-list-{os.urandom(8).hex()}.txt")

    try:
        # Asynchronously write the list of files to the temporary file
        async with aiofiles.open(list_file_path, mode="w", encoding="utf-8") as f:
            for path in file_paths:
                await f.write(f"file '{os.path.abspath(path)}'\n")

        # Construct the ffmpeg command
        command = [
            ffmpeg_executable,
            "-y",  # Overwrite output file if it exists
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file_path,
            "-c",
            "copy",
            output_path,
        ]

        print(f"Running async ffmpeg command: {' '.join(command)}")

        # Execute the command asynchronously
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Wait for the process to complete and capture output
        stdout, stderr = await process.communicate()

        # Check if ffmpeg exited with an error
        if process.returncode:
            # Decode stderr for a more useful error message
            # error_message = stderr.decode().strip()
            raise subprocess.CalledProcessError(
                returncode=process.returncode,
                cmd=command,
                output=stdout,
                stderr=stderr,
            )

        print("FFmpeg output:\n", stdout.decode())
        print("FFmpeg errors (if any):\n", stderr.decode())
        print(f"Successfully merged files into: {output_path}")

    except Exception as e:
        print(f"An error occurred during async merge: {e}")
        # Re-raise the exception to signal failure
        raise e
    finally:
        # Ensure the temporary list file is always deleted
        if os.path.exists(list_file_path):
            os.remove(list_file_path)

    return output_path
