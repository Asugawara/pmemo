from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

import openai
from prompt_toolkit.completion.base import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from pmemo.utils import sort_by_mtime


class OpenAiCompletion:
    """
    Wrapper class for OpenAI text completion using the OpenAI API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        **kwargs,
    ) -> None:
        """
        Initialize the OpenAiCompletion instance.

        Args:
            api_key (Optional[str]): The API key for accessing the OpenAI API.
            model (str): The model to use for text completion (default: "gpt-3.5-turbo").
            **kwargs: Additional keyword arguments to be passed to the OpenAI API.
        """
        self._api_key = api_key
        self._model = model
        self._kwargs = kwargs

    @lru_cache
    def request_chatgpt(self, prompt: str) -> str:
        """
        Request text completion from OpenAI Model based on the provided prompt.

        Args:
            prompt (str): The prompt to generate a completion for.

        Returns:
            str: The generated completion text.
        """
        if not prompt:
            return ""
        if openai.api_key is None and self._api_key is None:
            raise RuntimeError("OpenAI API key is missing or not provided")
        openai.api_key = openai.api_key or self._api_key
        completion = openai.ChatCompletion.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            **self._kwargs,
        )
        return completion.choices[0].message.content


class PromptTemplateCompleter(Completer):
    """
    A completer that provides prompt template suggestions based on existing template files.
    """

    def __init__(self, out_dir: Path) -> None:
        self._templates_dir = out_dir / "templates"
        self._templates = {
            file.stem: file for file in sort_by_mtime(self._templates_dir, "*.txt")
        }

    @property
    def templates(self) -> dict[str, Path]:
        return self._templates

    @property
    def templates_dir(self) -> Path:
        return self._templates_dir

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        for title, prompt in self._templates.items():
            yield Completion(text=prompt.read_text(), display=title)


def register_prompt_template(templates_dir: Path, title: str, prompt: str) -> None:
    """
    Register a prompt template by creating or updating a template file.

    Args:
        templates_dir (Path): The directory where template files are stored.
        title (str): The title of the template.
        prompt (str): The content of the template.
    """
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True)
    template_file = templates_dir / title
    template_file = template_file.with_suffix(".txt")
    if template_file.exists() and not prompt:
        template_file.unlink()
    else:
        template_file.write_text(prompt)
