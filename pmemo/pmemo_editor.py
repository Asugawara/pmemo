from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text.utils import to_plain_text
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.markup import MarkdownLexer
from pygments.styles import get_style_by_name

from pmemo.openai_completion import OpenAiCompletion
from pmemo.utils import error_handler


class AutoSuggestFromHistoryForMultiline(AutoSuggest):
    """
    Auto-suggests based on the lines in the input history for multiline input.
    """

    def get_suggestion(
        self, buffer: Buffer, document: Document
    ) -> Optional[Suggestion]:
        # Consider only the last line for the suggestion.
        text = document.text.rsplit("\n", 1)[-1]

        # Only create a suggestion when this is not an empty line.
        if text.strip():
            # Find first matching line in history.
            for string in reversed(list(buffer.history.get_strings())):
                if string.startswith(text):
                    return Suggestion(string[len(text) :])

        return None


class PmemoEditor:
    """A prompt-based memo editor with text input"""

    BRACKETS = {"(": ")", "{": "}", "[": "]", "（": "）", "『": "』", "「": "」"}
    INSTRUCTION = "(exit with 'Esc -> Enter')"

    def __init__(
        self,
        prompt_spaces: int = 4,
        style_name: str = "github-dark",
        indentation_spaces: int = 4,
        openai_completion: Optional[OpenAiCompletion] = None,
    ) -> None:
        """
        Initializes a PmemoEditor instance.

        Args:
            prompt_spaces (int, optional): The number of spaces for the prompt width. Defaults to 4.
            style_name (str, optional): The name of the style for syntax highlighting. Defaults to "github-dark".
            indentation_spaces (int, optional): The number of spaces for indentation. Defaults to 4.
        """
        self._prompt_spaces = prompt_spaces
        self._style = style_from_pygments_cls(get_style_by_name(style_name))
        self._content = None
        Char.display_mappings["\t"] = " " * indentation_spaces
        Char.display_mappings["\n"] = " "

        self._openai_completion = openai_completion

    def _ljust_line_number(self, line_number: int) -> str:
        line_number_str = str(line_number + 1)
        return line_number_str.ljust(self._prompt_spaces, " ")

    def _prompt_continuation(self, width, line_number, wrap_count) -> str:
        return self._ljust_line_number(line_number)

    def _build_prompt_message(self, message: str) -> str:
        instruction = "\n".join((self.INSTRUCTION, self._ljust_line_number(0)))
        return " ".join((message, instruction)) if message else instruction

    @error_handler
    def text(self, message: str, default: str = "", **kwargs) -> str:
        """
        Displays a prompt for text input with customizable message and default value.

        Args:
            message (str): The prompt message.
            default (str, optional): The default value to display and return. Defaults to "".
            **kwargs: Additional keyword arguments for PromptSession.

        Returns:
            str: The text input provided by the user.
        """
        session: PromptSession[str] = PromptSession(
            self._build_prompt_message(message),
            multiline=True,
            wrap_lines=True,
            mouse_support=True,
            key_bindings=self.get_key_bindings(),
            prompt_continuation=self._prompt_continuation,
            lexer=PygmentsLexer(MarkdownLexer),
            style=self._style,
            erase_when_done=True,
            auto_suggest=AutoSuggestFromHistoryForMultiline(),
            complete_while_typing=False,
            **kwargs,
        )
        session.default_buffer.reset(Document(default))
        return to_plain_text(session.app.run()).strip()

    def get_key_bindings(self) -> KeyBindingsBase:
        bindings = KeyBindings()

        @bindings.add(Keys.Tab)
        def _(event):
            event.app.current_buffer.insert_text("\t")

        @bindings.add(Keys.ControlD)
        def _(event):
            event.app.current_buffer.delete()

        @bindings.add(Keys.ControlZ)
        def _(event):
            event.app.current_buffer.undo()

        for bracket_start in self.BRACKETS:

            @bindings.add(bracket_start)
            def _(event):
                event.app.current_buffer.insert_text(event.data)
                event.app.current_buffer.insert_text(
                    self.BRACKETS[event.data], move_cursor=False
                )

        @bindings.add(Keys.ControlO)
        def _(event):
            if self._openai_completion is not None:
                data = event.app.current_buffer.copy_selection()
                completion = self._openai_completion.request_chatgpt(data.text)
                event.app.current_buffer.history.append_string(completion)
                event.app.current_buffer.suggestion = Suggestion(completion)

        @bindings.add(Keys.ControlI)
        def _(event):
            current_buffer = event.app.current_buffer
            if current_buffer.complete_state:
                current_buffer.complete_next()
            else:
                current_buffer.start_completion(select_first=False)

        return bindings
