![image](https://github.com/Asugawara/pmemo/actions/workflows/run_test.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/pmemo?color=green)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pmemo)
![GitHub](https://img.shields.io/github/license/Asugawara/pmemo)


# Pmemo(Prompt/Python memo)

**Pmemo** is a command-line memo(notepad) application that allows seamless editing directly in the terminal, without opening in full-screen mode like traditional text editors.<br>
Additionally, it provides the functionality to query the selected text to OpenAI's ChatGPT by using `ctrl + o` as a shortcut,
transforming it into a prompt for interactive inquiries.

![](https://github.com/Asugawara/pmemo/blob/main/pmemo.gif)

# Installation

```bash
$ pip install pmemo
```

# Usage

command | description
-- | --
`pm` or `pm new` | create new memo
`pm edit` | edit memo (searching with a specified query, similar to using the `peco`)
`pm list` | list all memos
`pm preview` | preview memo(markdown) on terminal (searching with a specified query, similar to using the `peco`)
`pm preference` | please refer to the [Preference section](https://github.com/Asugawara/pmemo#Preference)


# Preference

name | default | description
-- | -- | --
out_dir | `$HOME/.pmemo` | specifies the directory where Pmemo saves memos
memo_preference.max_title_length | 30 | sets the maximum length of a memo title
editor_preference.prompt_spaces | 4 | defines the number of spaces used for line numbering in the editor
editor_preference.style_name | "github-dark" | sets the style of the editor
editor_preference.indentation_spaces | 4 | sets the number of spaces for indentation (tab size)
openai_preference.api_key | None | The OpenAI API uses API keys for authentication
openai_preference.model | "gpt-3.5-turbo" | ID of the model to use
openai_preference.max_tokens | 16 | the maximum number of tokens to generate in the completion
openai_preference.temperature | 0 | what sampling temperature to use, between 0 and 2
openai_preference.n | 1 | how many completions to generate for each prompt


# Versioning
This repo uses [Semantic Versioning](https://semver.org/).

# License
**pmemo** is released under the MIT License. See [LICENSE](/LICENSE) for additional details.
