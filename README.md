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
```
usage: pm [-h] [-o OUTDIR] {new,edit,list,preview} ...

positional arguments:
  {new,edit,list,preview}
    new                 create new memo (default positional argument `pm` -> `pm new`)
    edit                edit memo (searching with a specified query, similar to using the `peco`)
    list                list all memos
    preview             preview memo(markdown) on terminal (searching with a specified query, similar to using the `peco`)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTDIR, --outdir OUTDIR
                        directory to save memos. default to $HOME/.pmemo
```

# Versioning
This repo uses [Semantic Versioning](https://semver.org/).

# License
**pmemo** is released under the MIT License. See [LICENSE](/LICENSE) for additional details.
