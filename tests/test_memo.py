from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from pmemo.memo import LANG_EXT, Memo, extract_codeblocks


@pytest.mark.parametrize(
    "lang_blockname",
    [
        "python",
        "python:test",
        "python: test",
        "go",
        "go:test",
        "go: test",
        "",
        " : ",
        " : test",
        "python: ",
    ],
)
@pytest.mark.parametrize(
    "code", ['print("hoge")', 'print("hoge")\n', '\nprint("hoge")', ""]
)
def test_extract_codeblock(lang_blockname, code):
    content = f"""
    test content

    ```{lang_blockname}
    {code}
    ```

    """
    extracted_lang, extracted_blockname, extracted_code = extract_codeblocks(content)[0]
    assert extracted_blockname
    assert extracted_blockname.endswith(LANG_EXT.get(extracted_lang, ""))
    assert extracted_code == code.strip()


@pytest.mark.parametrize(
    "lang_blockname",
    [
        "python",
        "python:test",
        "python: test",
        "go",
        "go:test",
        "go: test",
        "",
        " : ",
        " : test",
        "python: ",
    ],
)
@pytest.mark.parametrize(
    "code", ['print("hoge")', 'print("hoge")\n', '\nprint("hoge")', ""]
)
def test_extract_multi_codeblock(lang_blockname, code):
    content = f"""
    test content

    ```{lang_blockname}
    {code}
    ```

    hoge

    ```{lang_blockname}
    {code}
    ```

    fuga

    ```{lang_blockname}
    {code}
    ```

    """
    for extracted_lang, extracted_blockname, extracted_code in extract_codeblocks(
        content
    ):
        assert extracted_blockname
        assert extracted_blockname.endswith(LANG_EXT.get(extracted_lang, ""))
        assert extracted_code == code.strip()


@pytest.mark.parametrize(
    "content",
    ["", "test", "test\nnewline", "# has space", "tooooooooooooo loooooooooooooong"],
)
def test_memo_construct(content):
    with TemporaryDirectory() as tmp_outdir:
        tmp_dir = Path(tmp_outdir)
        memo1 = Memo(tmp_dir, content)
        (tmp_dir / "test").mkdir(parents=True)
        tmp_file = tmp_dir / "test" / "test.md"
        tmp_file.write_text(content)
        memo2 = Memo.from_file(tmp_file)
        assert isinstance(memo1, Memo)
        assert isinstance(memo2, Memo)
        assert memo1.content == memo2.content


@pytest.mark.parametrize(
    "content,title",
    [
        ("", "Untitled"),
        ("test", "test"),
        ("test\nnewline", "test"),
        ("# has space", "#_has_space"),
        ("tooooooooooooo loooooooooooooong", "tooooooooooooo_loooooooooooooo"),
    ],
)
def test_memo_properties(content, title):
    with TemporaryDirectory() as tmp_outdir:
        memo = Memo(Path(tmp_outdir), content)
        assert memo.title == title
        assert memo.file_path.stem == memo.title
        assert memo.file_path.parent.name == memo.title
        assert memo.file_path.suffix == ".md"
        assert memo.content == content


@pytest.mark.parametrize(
    "content",
    ["", "test", "test\nnewline", "# has space", "tooooooooooooo loooooooooooooong"],
)
def test_memo_edit(content):
    with TemporaryDirectory() as tmp_outdir:
        memo = Memo(Path(tmp_outdir), content)
        assert memo.content == content

        memo.edit_content(content)
        assert memo.content == content
        assert not memo._is_edited

        edited_content = "".join((content, "edit"))
        memo.edit_content(edited_content)
        assert memo.content == edited_content
        assert memo._is_edited


@pytest.mark.parametrize(
    "content",
    ["", "test", "test\nnewline", "# has space", "tooooooooooooo loooooooooooooong"],
)
def test_memo_save(content):
    with TemporaryDirectory() as tmp_outdir:
        memo = Memo(Path(tmp_outdir), content)
        memo.save()
        assert memo.file_path.exists()
        with patch("pmemo.utils.confirm", return_value=True):
            edited_content = "".join((content, "edit"))
            memo.edit_content(edited_content)
            memo.save()
            assert memo.file_path.read_text() != content
            assert memo.file_path.read_text() == edited_content

            memo.edit_content("")
            memo.save()
            assert memo.file_path.read_text() == ""


@pytest.mark.parametrize(
    "content",
    ["", "test", "test\nnewline", "# has space", "tooooooooooooo loooooooooooooong"],
)
def test_memo_nosave(content):
    with TemporaryDirectory() as tmp_outdir:
        memo = Memo(Path(tmp_outdir), content)
        memo.save()
        with patch("pmemo.utils.confirm", return_value=False):
            edited_content = "".join((content, "edit"))
            memo.edit_content(edited_content)
            memo.save()
            assert memo.file_path.read_text() == content
            assert memo.file_path.read_text() != edited_content

            memo.edit_content("")
            memo.save()
            assert memo.file_path.exists()
            assert memo.file_path.read_text() == content
            assert memo.file_path.read_text() != edited_content
