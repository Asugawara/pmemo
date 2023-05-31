import argparse
import copy
import subprocess

from rich.console import Console
from rich.markdown import Markdown

from pmemo.custom_select import custom_select
from pmemo.memo import Memo
from pmemo.openai_completion import (
    OpenAiCompletion,
    PromptTemplateCompleter,
    register_prompt_template,
)
from pmemo.pmemo_editor import PmemoEditor
from pmemo.preferences import PREFERENCE_FILE_PATH, PmemoPreference
from pmemo.utils import error_handler, sort_by_mtime


@error_handler
def update_preference(editor: PmemoEditor, preferences: dict) -> dict:
    selected = custom_select(list(preferences))
    if isinstance(preferences[selected], dict):
        update_preference(editor, preferences[selected])
        return preferences
    new_val = editor.text(
        f"{selected} = {preferences[selected]} -> ",
        str(preferences[selected]),
        multiline=False,
    )
    if new_val:
        preferences[selected] = new_val
    return preferences


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")
    parser_new = subparsers.add_parser(
        "new", help="create new memo (default positional argument `pm` -> `pm new`)"
    )
    parser_edit = subparsers.add_parser(
        "edit",
        help="edit memo (searching with a specified query, similar to using the `peco`)",
    )
    parser_list = subparsers.add_parser("list", help="list all memos")
    parser_list.add_argument("-p", "--prefix", type=str, default="")
    parser_preview = subparsers.add_parser(
        "preview",
        help="preview memo(markdown) on terminal (searching with a specified query, similar to using the `peco`)",
    )
    parser_preferences = subparsers.add_parser("preference", help="set preferences")
    parser_preferences.add_argument("--init", action="store_true")
    parser_templates = subparsers.add_parser(
        "template", help="register/edit prompt templates"
    )
    parser_templates.add_argument("-e", "--edit", action="store_true")
    parser_run = subparsers.add_parser("run", help="run codeblock")
    parser.set_defaults(cmd="new")
    args = parser.parse_args()

    preferences = (
        PmemoPreference.parse_file(PREFERENCE_FILE_PATH)
        if PREFERENCE_FILE_PATH.exists()
        else PmemoPreference()
    )

    completer = PromptTemplateCompleter(preferences.out_dir)

    editor = PmemoEditor(
        **preferences.editor_preference.dict(),
        openai_completion=OpenAiCompletion(**preferences.openai_preference.dict()),
    )
    if args.cmd == "new":
        content = editor.text("Memo", completer=completer)
        memo = Memo(
            preferences.out_dir,
            content,
            title_max_length=preferences.memo_preference.max_title_length,
        )
        memo.save()

    elif args.cmd == "edit":
        candidates = {
            p.name.strip(): p for p in sort_by_mtime(preferences.out_dir, "*/*.md")
        }
        edit_file_name = custom_select(choices=candidates)
        file_path = candidates[edit_file_name]
        memo = Memo.from_file(file_path, preferences.memo_preference.max_title_length)
        content = editor.text(
            f"Edit: {file_path.name}", default=memo.content, completer=completer
        )
        memo.edit_content(content)
        memo.save()

    elif args.cmd == "list":
        candidates = sort_by_mtime(preferences.out_dir, "*/*.md")
        candidates = [p.name for p in candidates if p.name.startswith(args.prefix)]
        print("\n".join(candidates))

    elif args.cmd == "preview":
        candidates = {
            p.name.strip(): p for p in sort_by_mtime(preferences.out_dir, "*/*.md")
        }
        edit_file_name = custom_select(choices=candidates)
        file_path = candidates[edit_file_name]
        console = Console()
        memo_content = Markdown(file_path.read_text())
        console.print(memo_content)

    elif args.cmd == "preference":
        if args.init:
            new_preferences = PmemoPreference()
        else:
            new_preferences_dict = update_preference(
                editor, copy.deepcopy(preferences.dict())
            )
            new_preferences = PmemoPreference.parse_obj(new_preferences_dict)
        new_preferences.write()

    elif args.cmd == "template":
        if args.edit:
            prompt_title = custom_select(completer.templates)
            file_path = completer.templates[prompt_title]
            prompt_text = editor.text(
                f"Edit: {file_path.name}", default=file_path.read_text()
            )
        else:
            prompt_title = editor.text("Prompt Title:", multiline=False)
            prompt_text = editor.text("Prompt Text")
        register_prompt_template(completer.templates_dir, prompt_title, prompt_text)

    elif args.cmd == "run":
        memo_title_candidates = [
            p.parent.name.strip() for p in sort_by_mtime(preferences.out_dir, "*/*.py")
        ]
        memo_title = custom_select(memo_title_candidates)
        codeblock_candidates = {
            p.name.strip(): p
            for p in sort_by_mtime(preferences.out_dir / memo_title, "*.py")
        }
        if not codeblock_candidates:
            return
        target_file = custom_select(codeblock_candidates)
        subprocess.run(["python3", preferences.out_dir / memo_title / target_file])

    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
