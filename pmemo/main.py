import argparse
import copy

from prompt_toolkit import PromptSession
from rich.console import Console
from rich.markdown import Markdown

from pmemo.custom_select import custom_select
from pmemo.memo import Memo
from pmemo.openai_completion import OpenAiCompletion
from pmemo.pmemo_editor import PmemoEditor
from pmemo.preferences import PREFERENCE_FILE_PATH, PmemoPreference
from pmemo.utils import error_handler, sort_memos_by_mtime


@error_handler
def update_preference(preferences: dict) -> dict:
    selected = custom_select(list(preferences))
    if isinstance(preferences[selected], dict):
        update_preference(preferences[selected])
        return preferences
    session: PromptSession[str] = PromptSession(
        f"{selected} = {preferences[selected]} -> "
    )
    preferences[selected] = session.app.run()
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
    parser.set_defaults(cmd="new")
    args = parser.parse_args()

    preferences = (
        PmemoPreference.parse_file(PREFERENCE_FILE_PATH)
        if PREFERENCE_FILE_PATH.exists()
        else PmemoPreference()
    )

    editor = PmemoEditor(
        **preferences.editor_preference.dict(),
        openai_completion=OpenAiCompletion(**preferences.openai_preference.dict()),
    )
    if args.cmd == "new":
        content = editor.text("Memo")
        memo = Memo(
            preferences.out_dir,
            content,
            title_max_length=preferences.memo_preference.max_title_length,
        )
        memo.save()

    elif args.cmd == "edit":
        candidates = {
            p.name.strip(): p for p in sort_memos_by_mtime(preferences.out_dir)
        }
        edit_file_name = custom_select(choices=candidates)
        file_path = candidates[edit_file_name]
        memo = Memo.from_file(file_path, preferences.memo_preference.max_title_length)
        content = editor.text(f"Edit: {file_path.name}", default=memo.content)
        memo.edit_content(content)
        memo.save()

    elif args.cmd == "list":
        candidates = sort_memos_by_mtime(preferences.out_dir)
        candidates = [p.name for p in candidates if p.name.startswith(args.prefix)]
        print("\n".join(candidates))

    elif args.cmd == "preview":
        candidates = {
            p.name.strip(): p for p in sort_memos_by_mtime(preferences.out_dir)
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
            new_preferences_dict = update_preference(copy.deepcopy(preferences.dict()))
            new_preferences = PmemoPreference.parse_obj(new_preferences_dict)
        new_preferences.write()

    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
