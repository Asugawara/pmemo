from pathlib import Path
from typing import Iterable

from prompt_toolkit.completion.base import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.keys import Keys

from pmemo.extensions.base import ExtensionBase
from pmemo.utils import sort_by_mtime


class PromptTemplateCompleter(Completer, ExtensionBase):
    """
    A completer that provides prompt template suggestions based on existing template files.
    """

    def __init__(self, out_dir: Path, key_binding: Keys = Keys.ControlT) -> None:
        self._templates_dir = out_dir / "templates"
        self._templates = {
            file.stem: file for file in sort_by_mtime(self._templates_dir, "*.txt")
        }
        self._key_binding = key_binding

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

    def get_key_bindings(self) -> KeyBindingsBase:
        bindings = KeyBindings()

        @bindings.add(self._key_binding)
        def display_registered_templates(event):
            buffer = event.app.current_buffer
            if buffer.complete_state:
                buffer.complete_next()
            else:
                buffer.start_completion(select_first=False)

        return bindings


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
