from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text.utils import to_plain_text
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.markup import MarkdownLexer
from pygments.styles import get_style_by_name

from pmemo.utils import error_handler


class PmemoEditor:
    """A prompt-based memo editor with text input"""

    BRACKETS = {"(": ")", "{": "}", "[": "]", "（": "）", "『": "』", "「": "」"}
    INSTRUCTION = "(exit with 'Esc -> Enter')"

    def __init__(
        self,
        prompt_spaces: int = 4,
        style_name: str = "github-dark",
        indentation_spaces: int = 4,
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
            mouse_support=True,
            key_bindings=self.get_key_bindings(),
            prompt_continuation=self._prompt_continuation,
            lexer=PygmentsLexer(MarkdownLexer),
            style=self._style,
            erase_when_done=True,
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

        return bindings
