![image](https://github.com/Asugawara/pmemo/actions/workflows/run_test.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/pmemo?color=green)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pmemo)
![GitHub](https://img.shields.io/github/license/Asugawara/pmemo)


# Pmemo(Prompt/Python memo)

CUI memo editor. No fullscreen and no transition but syntax highlighting.
![](https://github.com/Asugawara/pmemo/blob/main/pmemo.gif)

# Installation

```bash
$ pip install pmemo
```

# Usage

command | option | description
-- | -- | --
`pm` or `pm new` | -- | create new memo
`pm edit` | -- | edit memo (searching with a specified query, similar to using the `peco`)
`pm list` | -p, --prefix | list all memos
`pm preview` | -- | preview memo(markdown) on terminal (searching with a specified query, similar to using the `peco`)
`pm preference` | -- | please refer to the [Preference section](https://github.com/Asugawara/pmemo#Preference)


# Preference

name | default | help
-- | -- | --
out_dir | `$HOME/.pmemo` | specifies the directory where Pmemo saves memos
memo_preference.max_title_length | 30 | sets the maximum length of a memo title.
editor_preference.prompt_spaces | 4 | defines the number of spaces used for line numbering in the editor
editor_preference.style_name | "github-dark" | sets the style of the editor
editor_preference.indentation_spaces | 4 | sets the number of spaces for indentation (tab size)


# Versioning
This repo uses [Semantic Versioning](https://semver.org/).

# License
**pmemo** is released under the MIT License. See [LICENSE](/LICENSE) for additional details.
