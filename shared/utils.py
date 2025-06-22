import os
import glob
import shutil
import sys


def format_prompt(prompt: str, args: dict[str, str]):
    """
    Format a prompt without touching the output format by using the replace method
    """

    ret = prompt
    for k, v in args.items():
        ret = ret.replace("{" + k + "}", v)

    return ret


def find_ffmpeg():
    """Checks if ffmpeg is in the system's PATH and returns its path.
    Handles both Windows and Unix-like systems.
    """
    # For Windows, check for ffmpeg.exe
    if sys.platform == 'win32':
        # First check the user's specific installation path
        user_ffmpeg_path = os.path.expanduser(os.path.join('~', 'ffmpeg', 'bin', 'ffmpeg.exe'))
        if os.path.isfile(user_ffmpeg_path):
            return user_ffmpeg_path
            
        # Then try the standard which method
        ffmpeg_path = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
        
        # If that fails, try common Windows install locations
        if ffmpeg_path is None:
            common_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\Program Files'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\Program Files (x86)'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
            ]
            for path in common_paths:
                if os.path.isfile(path):
                    ffmpeg_path = path
                    break
    else:
        # For Unix-like systems, use the standard which method
        ffmpeg_path = shutil.which("ffmpeg")
    
    if ffmpeg_path is None:
        raise FileNotFoundError(
            "ffmpeg not found. Please install ffmpeg and ensure it is in your system's PATH. "
            "On Windows, make sure ffmpeg.exe is properly installed and added to PATH."
        )
    
    return ffmpeg_path


def delete_files_by_pattern(
    directory: str,
    pattern: str,
    recursive=False,
    dry_run=True,
    verbose=True,
):
    """
    Deletes files in a directory that match a given glob pattern.

    Args:
        directory (str): The path to the directory to search in.
        pattern (str): The glob pattern to match filenames against (e.g., '*.tmp', 'log-*.txt').
        recursive (bool, optional): If True, searches subdirectories as well. Defaults to False.
        dry_run (bool, optional): If True, prints which files would be deleted without
                                  actually deleting them. Defaults to True for safety.
        verbose (bool, optional): If True, prints information about actions being taken.
                                  Defaults to True.

    Returns:
        list: A list of paths to the files that were (or would have been) deleted.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Error: The directory '{directory}' does not exist.")

    # Construct the full search path using the pattern
    # The '**' pattern is used for recursive searching
    if recursive:
        search_path = os.path.join(directory, "**", pattern)
    else:
        search_path = os.path.join(directory, pattern)

    if verbose:
        print(
            f"Searching for pattern '{pattern}' in '{directory}' (Recursive: {recursive})"
        )
        if dry_run:
            print("--- DRY RUN MODE: No files will be deleted. ---")

    deleted_files_list = []

    # Use glob to find all files matching the pattern
    # The 'recursive=True' argument requires the '**' in the path
    for filepath in glob.glob(search_path, recursive=recursive):
        # Ensure we only attempt to delete files, not directories that might match the pattern
        if os.path.isfile(filepath):
            try:
                if dry_run:
                    if verbose:
                        print(f"[DRY RUN] Would delete: {filepath}")
                else:
                    os.remove(filepath)
                    if verbose:
                        print(f"Deleted: {filepath}")

                deleted_files_list.append(filepath)

            except OSError as e:
                # Catch errors like permission denied
                if verbose:
                    print(f"Error deleting {filepath}: {e}", file=sys.stderr)

    if verbose:
        count = len(deleted_files_list)
        action = "would be" if dry_run else "were"
        print(f"\nSummary: Found {count} file(s) that {action} deleted.")

    return deleted_files_list
