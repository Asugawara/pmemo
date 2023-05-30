from unittest.mock import Mock

import pytest
from prompt_toolkit.input.ansi_escape_sequences import REVERSE_ANSI_SEQUENCES
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.keys import Keys
from prompt_toolkit.output import DummyOutput

from pmemo.pmemo_editor import (
    AutoSuggestFromHistoryForMultiline,
    PmemoEditor,
    Suggestion,
)


@pytest.mark.parametrize(
    "text,expect",
    [
        ("h", "oge"),
        ("f", "uga"),
        ("ho", "ge"),
        ("hog", "e"),
        ("test", "\nmulti\nline"),
        ("no-hit", None),
    ],
)
def test_autosuggest(text, expect):
    auto_suggest = AutoSuggestFromHistoryForMultiline()
    buffer_mock = Mock()
    buffer_mock.history.get_strings = lambda: ["hoge", "fuga", "test\nmulti\nline"]
    document_mock = Mock()
    document_mock.text = text
    suggestion = auto_suggest.get_suggestion(buffer_mock, document_mock)
    if isinstance(suggestion, Suggestion):
        assert suggestion.text == expect
    else:
        assert suggestion is None


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
        pipe_input.send_text(
            "".join(
                (
                    text,
                    REVERSE_ANSI_SEQUENCES[Keys.Escape],
                    REVERSE_ANSI_SEQUENCES[Keys.Enter],
                )
            )
        )
        content = editor.text("Test", input=pipe_input, output=DummyOutput())
        assert content == text.strip()


@pytest.mark.parametrize(
    "text", ["", "   ", "test", "   text", "\ntext", "test\nmulti\nlines"]
)
def test_editor_text_when_set_default(text):
    editor = PmemoEditor()
    with create_pipe_input() as pipe_input:
        pipe_input.send_text(
            "".join(
                (
                    text,
                    REVERSE_ANSI_SEQUENCES[Keys.Escape],
                    REVERSE_ANSI_SEQUENCES[Keys.Enter],
                )
            )
        )
        content = editor.text(
            "Test", default="default", input=pipe_input, output=DummyOutput()
        )
        assert content == "".join(("default", text)).strip()


def test_editor_text_cancel():
    editor = PmemoEditor()
    with create_pipe_input() as pipe_input:
        pipe_input.send_text(REVERSE_ANSI_SEQUENCES[Keys.ControlC])
        with pytest.raises(SystemExit) as e:
            editor.text("Test", input=pipe_input, output=DummyOutput())
        assert e.type == SystemExit


def test_completion():
    editor = PmemoEditor()
    with create_pipe_input() as pipe_input:
        for bracket_start, bracket_end in PmemoEditor.BRACKETS.items():
            pipe_input.send_text(
                "".join(
                    (
                        bracket_start,
                        REVERSE_ANSI_SEQUENCES[Keys.Escape],
                        REVERSE_ANSI_SEQUENCES[Keys.Enter],
                    )
                )
            )
            content = editor.text("Test", input=pipe_input, output=DummyOutput())
            assert content == "".join((bracket_start, bracket_end))
