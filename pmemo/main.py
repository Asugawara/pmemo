import argparse
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

from pmemo.custom_select import custom_select
from pmemo.memo import Memo
from pmemo.pmemo_editor import PmemoEditor

DEFAULT_OUT_DIR = Path.home() / ".pmemo"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--outdir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"directory to save memos. default to {DEFAULT_OUT_DIR}",
    )
    subparsers = parser.add_subparsers(dest="cmd")
    parser_new = subparsers.add_parser(
        "new", help="create new memo (default positional argument `pm` -> `pm new`)"
    )
    parser_edit = subparsers.add_parser(
        "edit",
        help="edit memo (searching with a specified query, similar to using the `peco`)",
    )
    parser_edit.add_argument("-p", "--prefix", type=str, default="")
    parser_list = subparsers.add_parser("list", help="list all memos")
    parser_list.add_argument("-p", "--prefix", type=str, default="")
    parser_preview = subparsers.add_parser(
        "preview",
        help="preview memo(markdown) on terminal (searching with a specified query, similar to using the `peco`)",
    )
    parser_preview.add_argument("-p", "--prefix", type=str, default="")
    parser.set_defaults(cmd="new")
    args = parser.parse_args()

    editor = PmemoEditor()
    if args.cmd == "new":
        content = editor.text("Memo")
        memo = Memo(args.outdir, content)
        memo.save()

    elif args.cmd == "edit":
        candidates = sorted(
            args.outdir.glob("*/*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        candidates = {
            p.name.strip(): p for p in candidates if p.name.startswith(args.prefix)
        }
        edit_file_name = custom_select(choices=candidates)
        file_path = candidates[edit_file_name]
        memo = Memo.from_file(file_path)
        content = editor.text(f"Edit: {file_path.name}", default=memo.content)
        memo.edit_content(content)
        memo.save()

    elif args.cmd == "list":
        candidates = sorted(
            args.outdir.glob("*/*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        candidates = [p.name for p in candidates if p.name.startswith(args.prefix)]
        print("\n".join(candidates))

    elif args.cmd == "preview":
        candidates = sorted(
            args.outdir.glob("*/*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        candidates = {
            p.name.strip(): p for p in candidates if p.name.startswith(args.prefix)
        }
        edit_file_name = custom_select(choices=candidates)
        file_path = candidates[edit_file_name]
        console = Console()
        memo_content = Markdown(file_path.read_text())
        console.print(memo_content)

    else:
        raise NotImplementedError


if __name__ == "__main__":
    main()
