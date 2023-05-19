from __future__ import annotations

import hashlib
import re
from pathlib import Path

from prompt_toolkit.shortcuts import confirm

RE_CODEBLOCK = re.compile(r"`{3}([^:\s]*):?(.*?)\n([\s\S]+?)`{3}")
MAX_LENGTH = 30
LANG_EXT = {"markdown": ".md", "python": ".py", "python3": ".py"}
DEFAULT_ENCODING = "utf-8"


def extract_codeblocks(text: str) -> list[tuple[str, str, str]]:
    """
    Extracts code blocks from the given text and returns a list of tuples representing the code blocks.

    Args:
        text (str): The input text from which code blocks are extracted.

    Returns:
        list[tuple[str, str, str]]: A list of tuples representing code blocks. Each tuple contains three elements:
                                    - lang (str): The language of the code block.
                                    - blockname (str): The name or identifier of the code block.
                                    - code (str): The actual code contained in the block.
    """
    codeblocks = []
    for lang, blockname, code in RE_CODEBLOCK.findall(text):
        lang = lang.strip() if lang else "python"
        blockname = (
            blockname.strip()
            if blockname.strip()
            else hashlib.sha256(bytes(code, DEFAULT_ENCODING)).hexdigest()[:MAX_LENGTH]
        )
        blockname = "".join((blockname, LANG_EXT.get(lang, "")))
        codeblocks.append((lang, blockname, code.strip()))
    return codeblocks


class Memo:
    """
    Represents a memo with content, title, and file-related operations.
    If the title is not specified, title and file_path depend on the content.

    Attributes:
        TITLE_MAX_LENGTH (int): The maximum length allowed for a memo title.
    """

    TITLE_MAX_LENGTH: int = 30

    def __init__(self, out_dir: Path, content: str, title: str = ""):
        """
        Initializes a Memo instance.

        Args:
            out_dir (Path): The output directory where the memo will be stored.
            content (str): The content of the memo.
            title (str, optional): The title of the memo. Defaults to an empty string.
        """
        self._out_dir = out_dir
        self._content = content
        self._title = title
        self._is_edited: bool = False

    @classmethod
    def from_file(cls, file_path: Path) -> Memo:
        """
        Creates a Memo instance from a file.

        Args:
            file_path (Path): The path to the file.

        Returns:
            Memo: A Memo instance created from the file.
        """
        return cls(file_path.parents[1], file_path.read_text(), file_path.stem)

    def edit_content(self, content: str) -> None:
        """
        Edits the content of the memo.

        Args:
            content (str): The new content of the memo.
        """
        self._is_edited = self._content != content
        self._content = content

    @property
    def content(self) -> str:
        return self._content

    @property
    def title(self) -> str:
        """
        Returns the title of the memo.

        If the title is not specified, it is derived from the first line of the content.

        Returns:
            str: The title of the memo.
        """
        if not self._title:
            self._title = (
                self._content.splitlines()[0][: self.TITLE_MAX_LENGTH].replace(" ", "_")
                if self._content
                else "Untitled"
            )
        return self._title

    @property
    def file_path(self) -> Path:
        """
        Returns the file path where the memo is stored.

        Returns:
            Path: The file path of the memo.
        """
        basename = "".join((self.title, LANG_EXT["markdown"]))
        memo_dir = self._out_dir / self.title
        memo_dir.mkdir(parents=True, exist_ok=True)
        return memo_dir / basename

    def _remove(self) -> None:
        if self.file_path.exists() and confirm(
            f"{self.file_path.parent.name}: Remove?"
        ):
            for file in self.file_path.parent.iterdir():
                if file.is_file():
                    file.unlink()
            self.file_path.parent.rmdir()

    def _confirm_overwrite(self) -> bool:
        if self.file_path.exists() and self._is_edited:
            return confirm(f"{self.file_path.name}: Overwrite?")
        return True

    def save(self) -> None:
        """
        Saves the memo to the file system, including associated code blocks.
        """
        if not self._content:
            self._remove()
        elif self._confirm_overwrite():
            self.file_path.write_text(self._content)

            for _, blockname, code in extract_codeblocks(self._content):
                codeblock_path = self.file_path.parent / blockname
                codeblock_path.write_text(code)
