from functools import wraps
from pathlib import Path

from prompt_toolkit.shortcuts import confirm


def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            exit()

    return wrapper


def sort_by_mtime(dir: Path, pattern: str) -> list[Path]:
    """
    Sorts files in a directory by modification time.

    Args:
        dir (Path): The directory path containing files.

    Returns:
        list: A sorted list of Path objects representing files, sorted in descending order based on modification time.

    """
    return sorted(dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)


def confirm_overwrite(file_path: Path) -> bool:
    if file_path.exists():
        return confirm(f"{file_path.name}: Overwrite?")
    return True


def confirm_remove(file_path: Path) -> bool:
    if file_path.exists():
        return confirm(f"{file_path.name}: Remove?")
    return False


def read_head(file_path: Path, n: int = 5) -> list[str]:
    head = []
    with file_path.open("r") as f:
        for i, line in enumerate(f):
            if i == n:
                break
            head.append(line)
    return head
