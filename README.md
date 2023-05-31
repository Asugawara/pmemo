![image](https://github.com/Asugawara/pmemo/actions/workflows/run_test.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/pmemo?color=green)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pmemo)
![GitHub](https://img.shields.io/github/license/Asugawara/pmemo)


# Pmemo

**Pmemo** is a command-line memo editor designed for seamless editing directly in the terminal environment. It offers a range of features to enhance your memo-taking experience and leverages the power of OpenAI's ChatGPT.

![](https://github.com/Asugawara/pmemo/blob/main/pmemo.gif)

# Features
- Rebind `ctrl-o` to request to **ChatGPT**
- Rebind `ctrl-t` to quickly access frequently used registered prompts
- CUI memo application that allows seamless editing directly in the terminal
- No fullscreen mode, keeping your workflow within the terminal
- Efficient search functionality for your memos
- Easily customizable to fit your preferences
- Execute code blocks written by you or ChatGPT immediately (Python only)

# Installation

```bash
$ pip install pmemo
```

# Usage

command | description
-- | --
`pm` or `pm new` | create new memo
`pm edit` | edit memo
`pm list` | list all memos
`pm preview` | preview memo(markdown) on terminal
`pm preference` | please refer to the [Preference section](https://github.com/Asugawara/pmemo#Preference)
`pm template` | create a new prompt template for completion usingh `ctrl-t`
`pm template -e` | edit an existing prompt template.
`pm run` | execute code blocks within your memos.


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

Note: To enable ChatGPT functionality, make sure to set your OpenAI API key as an environment variable or preference.

# Versioning
This repo uses [Semantic Versioning](https://semver.org/).

# License
**pmemo** is released under the MIT License. See [LICENSE](/LICENSE) for additional details.
