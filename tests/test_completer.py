from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from prompt_toolkit.completion.base import CompleteEvent, Completion
from prompt_toolkit.document import Document

from pmemo.extensions.prompt_template_manager import (
    PromptTemplateCompleter,
    register_prompt_template,
)


def test_prompt_template_completer():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        # Add sample template files for testing
        templates_dir = tmp_dir / "templates"
        templates_dir.mkdir()
        template1 = templates_dir / "template1.txt"
        template1.write_text("This is template 1")
        template2 = templates_dir / "template2.txt"
        template2.write_text("This is template 2")

        template_completer = PromptTemplateCompleter(tmp_dir)

        # Test the templates property
        assert len(template_completer.templates) == 2
        assert "template1" in template_completer.templates
        assert "template2" in template_completer.templates

        # Test the templates_dir property
        assert template_completer.templates_dir == tmp_dir / "templates"

        # Test the get_completions method
        completions = list(
            template_completer.get_completions(Document(), CompleteEvent())
        )
        assert len(completions) == 2
        assert all(isinstance(c, Completion) for c in completions)


def test_no_prompt_template():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        template_completer = PromptTemplateCompleter(tmp_dir)

        assert len(template_completer.templates) == 0
        assert not template_completer.templates


def test_register_prompt_template():
    # Test registering a new prompt template
    TEMPLATE_TITLE = "new_template"
    with TemporaryDirectory() as tmp_dir:
        template_dir = Path(tmp_dir) / "templates"
        TEMPLATE_PROMPT = "This is a new template"
        register_prompt_template(template_dir, TEMPLATE_TITLE, TEMPLATE_PROMPT)
        template_file = template_dir / (TEMPLATE_TITLE + ".txt")
        assert template_file.exists()
        assert template_file.read_text() == TEMPLATE_PROMPT

        # Test updating an existing prompt template
        UPDATED_PROMPT = "This is an updated template"
        register_prompt_template(template_dir, TEMPLATE_TITLE, UPDATED_PROMPT)
        assert template_file.exists()
        assert template_file.read_text() == UPDATED_PROMPT

        # Test deleting a prompt template
        register_prompt_template(template_dir, TEMPLATE_TITLE, "")
        assert not template_file.exists()
