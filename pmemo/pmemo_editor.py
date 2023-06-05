from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from prompt_toolkit.completion import Completer, merge_completers
from prompt_toolkit.document import Document
from prompt_toolkit.filters import has_selection
from prompt_toolkit.formatted_text.utils import to_plain_text
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.screen import Char
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.lexers.markup import MarkdownLexer
from pygments.styles import get_style_by_name

from pmemo.extensions.base import ExtensionBase
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
        extensions: Optional[list[ExtensionBase]] = None,
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
        Char.display_mappings["\t"] = " " * indentation_spaces
        Char.display_mappings["\n"] = " "

        self._extensions = extensions

    def _ljust_line_number(self, line_number: int) -> str:
        line_number_str = str(line_number + 1)
        return line_number_str.ljust(self._prompt_spaces, " ")

    def _prompt_continuation(self, width, line_number, wrap_count) -> str:
        return self._ljust_line_number(line_number)

    def _build_prompt_message(self, message: str, multiline: bool = True) -> str:
        if not multiline:
            return message
        instruction = "\n".join((self.INSTRUCTION, self._ljust_line_number(0)))
        return " ".join((message, instruction)) if message else instruction

    @error_handler
    def text(
        self, message: str, default: str = "", multiline: bool = True, **kwargs
    ) -> str:
        """
        Displays a prompt for text input with customizable message and default value.

        Args:
            message (str): The prompt message.
            default (str, optional): The default value to display and return. Defaults to "".
            multiline (bool): When True, prefer a layout that is more adapted for multiline input.
            **kwargs: Additional keyword arguments for PromptSession.

        Returns:
            str: The text input provided by the user.
        """
        key_bindings = self.get_key_bindings()
        completer = None
        if self._extensions is not None:
            key_bindings = merge_key_bindings(
                [key_bindings, *[e.get_key_bindings() for e in self._extensions]]
            )
            completer = merge_completers(
                [e for e in self._extensions if isinstance(e, Completer)]
            )
        session: PromptSession[str] = PromptSession(
            self._build_prompt_message(message, multiline),
            multiline=multiline,
            wrap_lines=True,
            mouse_support=True,
            key_bindings=key_bindings,
            prompt_continuation=self._prompt_continuation,
            lexer=PygmentsLexer(MarkdownLexer),
            style=self._style,
            erase_when_done=True,
            auto_suggest=AutoSuggestFromHistoryForMultiline(),
            clipboard=PyperclipClipboard(),
            complete_while_typing=False,
            completer=completer,
            **kwargs,
        )
        session.default_buffer.reset(Document(default))
        return to_plain_text(session.app.run()).strip()

    def get_key_bindings(self) -> KeyBindingsBase:
        bindings = KeyBindings()

        @bindings.add(Keys.Tab)
        def insert_tab(event):
            event.app.current_buffer.insert_text("\t")

        @bindings.add(Keys.ControlD)
        def delete_char(event):
            event.app.current_buffer.delete()

        @bindings.add(Keys.ControlZ)
        def undo(event):
            event.app.current_buffer.undo()

        for bracket_start in self.BRACKETS:

            @bindings.add(bracket_start)
            def _(event):
                event.app.current_buffer.insert_text(event.data)
                event.app.current_buffer.insert_text(
                    self.BRACKETS[event.data], move_cursor=False
                )

        @bindings.add(Keys.ControlA)
        def select_all(event):
            event.app.current_buffer.cursor_position = 0
            event.app.current_buffer.start_selection()
            event.app.current_buffer.cursor_position = len(
                event.app.current_buffer.text
            )

        @bindings.add(Keys.ControlL)
        def select_line(event):
            buffer = event.app.current_buffer
            buffer.cursor_position += buffer.document.get_start_of_line_position(
                after_whitespace=False
            )
            buffer.start_selection()
            buffer.cursor_position += buffer.document.get_end_of_line_position()

        @bindings.add(Keys.ControlL, filter=has_selection)
        def select_lines(event):
            event.current_buffer.cursor_down(count=event.arg)

        @bindings.add(Keys.Any, filter=has_selection)
        def replace_selection(event):
            event.current_buffer.cut_selection()
            event.current_buffer.insert_text(event.data * event.arg)

        @bindings.add(Keys.Backspace, filter=has_selection)
        def delete_selection(event):
            event.current_buffer.cut_selection()
            event.app.current_buffer.exit_selection()

        @bindings.add(Keys.Right, filter=has_selection)
        @bindings.add(Keys.Down, filter=has_selection)
        def exit_selection_cursor_end(event):
            event.app.current_buffer.exit_selection()

        @bindings.add(Keys.Left, filter=has_selection)
        @bindings.add(Keys.Up, filter=has_selection)
        def exit_selection_cursor_begin(event):
            buffer = event.app.current_buffer
            buffer.cursor_position = buffer.document.selection_range()[0]
            buffer.exit_selection()

        @bindings.add(Keys.ShiftRight, filter=has_selection)
        def move_selection_right(event):
            buffer = event.app.current_buffer
            line_end_position = (
                buffer.cursor_position + buffer.document.get_end_of_line_position()
            )
            if buffer.cursor_position != line_end_position:
                buffer.cursor_right(count=event.arg)
            else:
                buffer.cursor_down()

        @bindings.add(Keys.ShiftLeft, filter=has_selection)
        def move_selection_left(event):
            buffer = event.app.current_buffer
            line_start_position = (
                buffer.cursor_position + buffer.document.get_start_of_line_position()
            )
            if buffer.cursor_position != line_start_position:
                buffer.cursor_left(count=event.arg)
            else:
                buffer.cursor_up()

        @bindings.add(Keys.ShiftDown, filter=has_selection)
        def move_selection_down(event):
            event.app.current_buffer.cursor_down(count=event.arg)

        @bindings.add(Keys.ShiftUp, filter=has_selection)
        def move_selection_up(event):
            event.app.current_buffer.cursor_up(count=event.arg)

        @bindings.add(Keys.ControlX, filter=has_selection)
        def cut_selection(event):
            data = event.app.current_buffer.cut_selection()
            event.app.clipboard.set_data(data)

        @bindings.add(Keys.ControlC, filter=has_selection)
        def copy_selection(event):
            data = event.app.current_buffer.copy_selection()
            event.app.clipboard.set_data(data)

        @bindings.add(Keys.ControlV)
        def paste_selection(event):
            data = event.app.clipboard.get_data()
            event.app.current_buffer.paste_clipboard_data(data)

        return bindings
