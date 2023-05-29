from functools import wraps
from pathlib import Path


def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            exit()

    return wrapper


def sort_by_mtime(dir: Path, pattern: str) -> list:
    """
    Sorts files in a directory by modification time.

    Args:
        dir (Path): The directory path containing files.

    Returns:
        list: A sorted list of Path objects representing files, sorted in descending order based on modification time.

    """
    return sorted(dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
