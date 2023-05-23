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


def sort_memos_by_mtime(memo_dir: Path) -> list:
    """
    Sorts memo files in a directory by modification time.

    Args:
        memo_dir (Path): The directory path containing memo files.

    Returns:
        list: A sorted list of Path objects representing memo files, sorted in descending order based on modification time.

    """
    return sorted(
        memo_dir.glob("*/*.md"), key=lambda p: p.stat().st_mtime, reverse=True
    )
