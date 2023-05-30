from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from prompt_toolkit.input.ansi_escape_sequences import REVERSE_ANSI_SEQUENCES
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.keys import Keys
from prompt_toolkit.output import DummyOutput

from pmemo.custom_select import custom_select


def test_custom_select():
    with create_pipe_input() as pipe_input:
        pipe_input.send_text(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        selected = custom_select([], input=pipe_input, output=DummyOutput())
        assert selected == ""

        pipe_input.send_text(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        selected = custom_select(
            ["a", "b", "c"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "a"

        pipe_input.send_text(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        with pytest.raises(TypeError) as e:
            selected = custom_select([1, 2, 3], input=pipe_input, output=DummyOutput())


def test_custom_select_from_dict():
    with create_pipe_input() as pipe_input, TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        test1 = tmp_dir / "test1.txt"
        test1.write_text("")
        test2 = tmp_dir / "test2.txt"
        test2.write_text("")

        choices = {"test1": test1, "test2": test2}
        pipe_input.send_text(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        selected = custom_select(choices, input=pipe_input, output=DummyOutput())
        assert selected == "test1"

        choices = {"test1": "test1", "test2": "test2"}
        pipe_input.send_text(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        with pytest.raises(AttributeError) as e:
            selected = custom_select(choices, input=pipe_input, output=DummyOutput())


def test_custom_select_move_cursor():
    with create_pipe_input() as pipe_input:
        pipe_input.send_text(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        selected = custom_select(
            ["a", "b", "c"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "a"

        pipe_input.send_text(
            "".join(
                (REVERSE_ANSI_SEQUENCES[Keys.Down], REVERSE_ANSI_SEQUENCES[Keys.Enter])
            )
        )
        selected = custom_select(
            ["a", "b", "c"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "b"

        pipe_input.send_text(
            "".join(
                (
                    REVERSE_ANSI_SEQUENCES[Keys.Down] * 2,
                    REVERSE_ANSI_SEQUENCES[Keys.Enter],
                )
            )
        )
        selected = custom_select(
            ["a", "b", "c"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "c"

        pipe_input.send_text(
            "".join(
                (
                    REVERSE_ANSI_SEQUENCES[Keys.Down] * 3,
                    REVERSE_ANSI_SEQUENCES[Keys.Enter],
                )
            )
        )
        selected = custom_select(
            ["a", "b", "c"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "a"

        pipe_input.send_text(
            "".join(
                (REVERSE_ANSI_SEQUENCES[Keys.Up], REVERSE_ANSI_SEQUENCES[Keys.Enter])
            )
        )
        selected = custom_select(
            ["a", "b", "c"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "c"

        pipe_input.send_text(
            "".join(
                (
                    REVERSE_ANSI_SEQUENCES[Keys.Up] * 2,
                    REVERSE_ANSI_SEQUENCES[Keys.Enter],
                )
            )
        )
        selected = custom_select(
            ["a", "b", "c"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "b"

        pipe_input.send_text(
            "".join(
                (
                    REVERSE_ANSI_SEQUENCES[Keys.Up] * 3,
                    REVERSE_ANSI_SEQUENCES[Keys.Enter],
                )
            )
        )
        selected = custom_select(
            ["a", "b", "c"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "a"


def test_custom_select_using_filter():
    with create_pipe_input() as pipe_input, patch(
        "prompt_toolkit.widgets.TextArea.text", "a"
    ):
        pipe_input.send_text("".join((REVERSE_ANSI_SEQUENCES[Keys.Enter])))
        selected = custom_select(
            ["a", "b", "c", "aa"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "a"

        pipe_input.send_text(
            "".join(
                (REVERSE_ANSI_SEQUENCES[Keys.Down], REVERSE_ANSI_SEQUENCES[Keys.Enter])
            )
        )
        selected = custom_select(
            ["a", "b", "c", "aa"], input=pipe_input, output=DummyOutput()
        )
        assert selected == "aa"

    # no hit
    with create_pipe_input() as pipe_input, patch(
        "prompt_toolkit.widgets.TextArea.text", "z"
    ):
        pipe_input.send_text("".join((REVERSE_ANSI_SEQUENCES[Keys.Enter])))
        selected = custom_select(
            ["a", "b", "c", "aa"], input=pipe_input, output=DummyOutput()
        )
        assert selected == ""

        pipe_input.send_text(
            "".join(
                (REVERSE_ANSI_SEQUENCES[Keys.Down], REVERSE_ANSI_SEQUENCES[Keys.Enter])
            )
        )
        selected = custom_select(
            ["a", "b", "c", "aa"], input=pipe_input, output=DummyOutput()
        )
        assert selected == ""
