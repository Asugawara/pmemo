from functools import partial

from prompt_toolkit.application import Application
from prompt_toolkit.filters import IsDone
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.formatted_text.utils import to_plain_text
from prompt_toolkit.key_binding import KeyBindings, KeyBindingsBase, merge_key_bindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea

from pmemo.utils import error_handler

ITEM_CLASS = "class:item"
SELECTED_CLASS = "class:selected"
styles = Style([("item", ""), ("selected", "underline bg:#d980ff #ffffff")])


class CustomFormattedTextControl(FormattedTextControl):
    def __init__(self, text: AnyFormattedText, *args, **kwargs) -> None:
        super(CustomFormattedTextControl, self).__init__(
            self._convert_callable_text(text), *args, **kwargs
        )
        self.pointed_at = 0

    @property
    def choice_count(self) -> int:
        return len(self._fragments) if self._fragments is not None else 0

    def _convert_callable_text(self, text: AnyFormattedText) -> AnyFormattedText:
        if callable(text):

            def wrapper():
                choices = []
                for i, (style, item) in enumerate(text()):
                    if i == self.pointed_at:
                        choices.append((SELECTED_CLASS, item))
                    else:
                        choices.append((style, item))
                return choices

            return wrapper
        return text

    def move_cursor_up(self) -> None:
        self.pointed_at -= 1
        self.pointed_at = max(0, min(self.pointed_at, self.choice_count - 1))

    def move_cursor_down(self) -> None:
        self.pointed_at += 1
        self.pointed_at = max(0, min(self.pointed_at, self.choice_count - 1))

    def get_pointed_at(self) -> AnyFormattedText:
        self.pointed_at = max(0, min(self.pointed_at, self.choice_count - 1))
        return (
            self._fragments[self.pointed_at][1] if self._fragments is not None else None
        )

    def get_key_bindings(self) -> KeyBindingsBase:
        bindings = KeyBindings()

        @bindings.add(Keys.ControlC, eager=True)
        def _(event):
            event.app.exit(exception=KeyboardInterrupt, style="class:aborting")

        @bindings.add(Keys.Up)
        def _(event):
            self.move_cursor_up()

        @bindings.add(Keys.Down)
        def _(event):
            self.move_cursor_down()

        @bindings.add(Keys.Enter)
        def _(event):
            content = self.get_pointed_at()
            event.app.exit(content)

        return (
            bindings
            if self.key_bindings is None
            else merge_key_bindings([bindings, self.key_bindings])
        )


@error_handler
def custom_select(choices: list[str]) -> str:
    """Choose one option from a list of choices while searching with a specified query, similar to using the "peco"
    If the execution is interrupted by a "KeyboardInterrupt" (typically triggered by pressing Ctrl+C), the program will be terminated.

    Args:
        choices (list[str]): list of choices displayed on the terminal.

    Returns:
        str: string of the selected choice.
    """
    text_area = TextArea(prompt="QUERY> ", multiline=False)

    def filter_candidates(choices):
        input_text = text_area.text
        return [
            (ITEM_CLASS, "".join((item, "\n")))
            for item in choices
            if input_text in item
        ]

    control = CustomFormattedTextControl(
        partial(filter_candidates, choices), focusable=True
    )

    candidates_display = ConditionalContainer(Window(control), ~IsDone())

    app: Application[AnyFormattedText] = Application(
        layout=Layout(HSplit([text_area, candidates_display])),
        key_bindings=control.get_key_bindings(),
        style=styles,
        erase_when_done=True,
    )
    return to_plain_text(app.run()).strip()
