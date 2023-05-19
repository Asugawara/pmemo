import pytest
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from pmemo.pmemo_editor import PmemoEditor


def test_editor_line_number():
    editor = PmemoEditor(prompt_spaces=4)
    assert editor._ljust_line_number(0) == "".join(("1", " " * 3))
    assert editor._ljust_line_number(9) == "".join(("10", " " * 2))
    assert editor._ljust_line_number(99) == "".join(("100", " " * 1))
    assert editor._ljust_line_number(999) == "1000"
    assert editor._ljust_line_number(9999) == "10000"

    editor = PmemoEditor(prompt_spaces=5)
    assert editor._ljust_line_number(0) == "".join(("1", " " * 4))
    assert editor._ljust_line_number(9) == "".join(("10", " " * 3))
    assert editor._ljust_line_number(99) == "".join(("100", " " * 2))
    assert editor._ljust_line_number(999) == "".join(("1000", " " * 1))
    assert editor._ljust_line_number(9999) == "10000"


def test_editor_instruction():
    editor = PmemoEditor()
    assert (
        editor._build_prompt_message("Memo") == "Memo (exit with 'Esc -> Enter')\n1   "
    )
    assert editor._build_prompt_message("") == "(exit with 'Esc -> Enter')\n1   "


@pytest.mark.parametrize(
    "text", ["", "   ", "test", "   text", "\ntext", "test\nmulti\nlines"]
)
def test_editor_text(text):
    editor = PmemoEditor()
    with create_pipe_input() as pipe_input:
        pipe_input.send_text("".join((text, "\x1b\r")))
        content = editor.text("Test", input=pipe_input, output=DummyOutput())
        assert content == text.strip()


@pytest.mark.parametrize(
    "text", ["", "   ", "test", "   text", "\ntext", "test\nmulti\nlines"]
)
def test_editor_text_when_set_default(text):
    editor = PmemoEditor()
    with create_pipe_input() as pipe_input:
        pipe_input.send_text("".join((text, "\x1b\r")))
        content = editor.text(
            "Test", default="default", input=pipe_input, output=DummyOutput()
        )
        assert content == "".join(("default", text)).strip()


def test_editor_text_cancel():
    editor = PmemoEditor()
    with create_pipe_input() as pipe_input:
        pipe_input.send_text("\x03")
        with pytest.raises(SystemExit) as e:
            editor.text("Test", input=pipe_input, output=DummyOutput())
        assert e.type == SystemExit


def test_completion():
    editor = PmemoEditor()
    with create_pipe_input() as pipe_input:
        for bracket_start in PmemoEditor.BRACKETS:
            pipe_input.send_text("".join((bracket_start, "\x1b\r")))
            content = editor.text("Test", input=pipe_input, output=DummyOutput())
            assert content == "".join(
                (bracket_start, PmemoEditor.BRACKETS[bracket_start])
            )
