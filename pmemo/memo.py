from __future__ import annotations

import hashlib
import re
import sys
from difflib import context_diff
from pathlib import Path

from pmemo.utils import confirm_overwrite, confirm_remove

RE_CODEBLOCK = re.compile(r"`{3}([^:\s]*):?(.*?)\n([\s\S]+?)`{3}")
LANG_EXT = {"markdown": ".md", "python": ".py", "python3": ".py"}
DEFAULT_ENCODING = "utf-8"


def extract_codeblocks(
    text: str, title_max_length: int = 30
) -> list[tuple[str, str, str]]:
    """
    Extracts code blocks from the given text and returns a list of tuples representing the code blocks.

    Args:
        text (str): The input text from which code blocks are extracted.
        title_max_length (int): Max length of codeblock's title. Defaults to 30.

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
            else hashlib.sha256(bytes(code, DEFAULT_ENCODING)).hexdigest()[
                :title_max_length
            ]
        )
        blockname = "".join((blockname, LANG_EXT.get(lang, "")))
        codeblocks.append((lang, blockname, code.strip()))
    return codeblocks


class Memo:
    """
    Represents a memo with content, title, and file-related operations.
    If the title is not specified, title and file_path depend on the content.
    """

    def __init__(
        self, out_dir: Path, content: str, title: str = "", title_max_length: int = 30
    ):
        """
        Initializes a Memo instance.

        Args:
            out_dir (Path): The output directory where the memo will be stored.
            content (str): The content of the memo.
            title (str, optional): The title of the memo. Defaults to an empty string.
            title_max_length (int): Max length of codeblock's title. Defaults to 30.
        """
        self._out_dir = out_dir
        self._content = content
        self._title = title
        self._title_max_length = title_max_length
        self._is_edited: bool = False

    @classmethod
    def from_file(cls, file_path: Path, title_max_length: int = 30) -> Memo:
        """
        Creates a Memo instance from a file.

        Args:
            file_path (Path): The path to the file.
            title_max_length (int): Max length of codeblock's title. Defaults to 30.

        Returns:
            Memo: A Memo instance created from the file.
        """
        return cls(
            file_path.parents[1],
            file_path.read_text(),
            file_path.stem,
            title_max_length,
        )

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
                self._content.splitlines()[0][: self._title_max_length].replace(
                    " ", "_"
                )
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

    def remove(self) -> None:
        """
        Removes the memo.
        """
        if confirm_remove(self.file_path.parent):
            for file in self.file_path.parent.iterdir():
                if file.is_file():
                    file.unlink()
            self.file_path.parent.rmdir()

    def save(self, show_diff: bool = False) -> None:
        """
        Saves the memo to the file system, including associated code blocks.
        """
        if show_diff and self.file_path.exists():
            existing_content = self.file_path.read_text().splitlines(True)
            new_content = self._content.splitlines(True)
            sys.stderr.writelines(
                context_diff(
                    existing_content,
                    new_content,
                    fromfile=self.file_path.name,
                    tofile="pulled content",
                )
            )

        if confirm_overwrite(self.file_path):
            self.file_path.write_text(self._content)

            for _, blockname, code in extract_codeblocks(
                self._content, self._title_max_length
            ):
                codeblock_path = self.file_path.parent / blockname
                codeblock_path.write_text(code)
