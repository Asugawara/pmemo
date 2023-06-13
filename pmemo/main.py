import argparse
import copy
import subprocess

from rich.console import Console
from rich.markdown import Markdown

from pmemo.custom_select import custom_select, select_file
from pmemo.extensions.openai_completion import OpenAiCompletion
from pmemo.extensions.prompt_template_manager import (
    PromptTemplateCompleter,
    register_prompt_template,
)
from pmemo.memo import Memo
from pmemo.pmemo_editor import PmemoEditor
from pmemo.preferences import PREF_FILE_PATH, PmemoPref
from pmemo.utils import error_handler, sort_by_mtime


@error_handler
def update_pref(editor: PmemoEditor, pref: dict) -> dict:
    selected = custom_select(list(pref))
    if isinstance(pref[selected], dict):
        update_pref(editor, pref[selected])
        return pref
    new_val = editor.text(
        f"{selected} = {pref[selected]} -> ",
        str(pref[selected]),
        multiline=False,
    )
    if new_val:
        pref[selected] = new_val
    return pref


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")
    parser_new = subparsers.add_parser(
        "new", help="create new memo (default positional argument `pm` -> `pm new`)"
    )
    parser_edit = subparsers.add_parser(
        "edit",
        help="edit memo",
    )
    parser_remove = subparsers.add_parser(
        "remove",
        help="remove memo",
    )
    parser_list = subparsers.add_parser("list", help="list all memos")
    parser_list.add_argument("-p", "--prefix", type=str, default="")
    parser_preview = subparsers.add_parser(
        "preview",
        help="preview memo(markdown) on terminal",
    )
    parser_pref = subparsers.add_parser("pref", help="set pref")
    parser_pref.add_argument("--init", action="store_true")
    parser_templates = subparsers.add_parser(
        "template", help="register/edit prompt templates"
    )
    parser_templates.add_argument("-e", "--edit", action="store_true")
    parser_run = subparsers.add_parser("run", help="run codeblock")
    parser.set_defaults(cmd="new")
    args = parser.parse_args()

    pref = (
        PmemoPref.parse_file(PREF_FILE_PATH) if PREF_FILE_PATH.exists() else PmemoPref()
    )

    extensions = [
        PromptTemplateCompleter(pref.extensions_pref.template_pref.template_dir),
        OpenAiCompletion(**pref.extensions_pref.openai_pref.dict()),
    ]

    editor = PmemoEditor(
        **pref.editor_pref.dict(),
        extensions=extensions,
    )
    if args.cmd == "new":
        content = editor.text("Memo")
        memo = Memo(
            pref.out_dir,
            content,
            title_max_length=pref.memo_pref.max_title_length,
        )
        memo.save()

    elif args.cmd == "edit":
        file_path = select_file(pref.out_dir, "*/*.md")
        memo = Memo.from_file(file_path, pref.memo_pref.max_title_length)
        content = editor.text(f"Edit: {file_path.name}", default=memo.content)
        memo.edit_content(content)
        memo.save()

    elif args.cmd == "remove":
        file_path = select_file(pref.out_dir, "*/*.md")
        memo = Memo.from_file(file_path, pref.memo_pref.max_title_length)
        memo.remove()

    elif args.cmd == "list":
        candidates = sort_by_mtime(pref.out_dir, "*/*.md")
        candidates = [p.name for p in candidates if p.name.startswith(args.prefix)]
        print("\n".join(candidates))

    elif args.cmd == "preview":
        file_path = select_file(pref.out_dir, "*/*.md")
        console = Console()
        memo_content = Markdown(file_path.read_text())
        console.print(memo_content)

    elif args.cmd == "pref":
        if args.init:
            new_pref = PmemoPref()
        else:
            new_pref_dict = update_pref(editor, copy.deepcopy(pref.dict()))
            new_pref = PmemoPref.parse_obj(new_pref_dict)
        new_pref.write()

    elif args.cmd == "template":
        if args.edit:
            file_path = select_file(
                pref.extensions_pref.template_pref.template_dir, "*.txt"
            )
            prompt_text = editor.text(
                f"Edit: {file_path.name}", default=file_path.read_text()
            )
        else:
            prompt_title = editor.text("Prompt Title:", multiline=False)
            prompt_text = editor.text("Prompt Text")
        register_prompt_template(
            pref.extensions_pref.template_pref.template_dir, prompt_title, prompt_text
        )

    elif args.cmd == "run":
        memo_title_candidates = [
            p.parent.stem for p in sort_by_mtime(pref.out_dir, "*/*.py")
        ]
        memo_title = custom_select(memo_title_candidates)
        codeblock_candidates = {
            p.stem: p for p in sort_by_mtime(pref.out_dir / memo_title, "*.py")
        }
        if not codeblock_candidates:
            return
        target_file = custom_select(codeblock_candidates)
        subprocess.run(["python3", pref.out_dir / memo_title / target_file])

    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
