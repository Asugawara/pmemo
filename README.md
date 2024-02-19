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
- Unrestricted access and management of memos, whether on local machine, remote server or different environments.

# Installation

```bash
$ pip install pmemo
```

# Usage

command | description
-- | --
`pm` or `pm new` | create new memo
`pm edit` | edit memo
`pm remove` | remove memo
`pm list` | list all memos
`pm preview` | preview memo(markdown) on terminal
`pm preference` | please refer to the [Preference section](https://github.com/Asugawara/pmemo#Preference)
`pm template` | create a new prompt template for completion using `ctrl-t`
`pm template -e` | edit an existing prompt template.
`pm run` | execute code blocks within your memos.
`pm signup` | create new account in the system. (requires email and password)
`pm login` | log into the existing account.
`pm push` | push local memos to the pmemo_server
`pm pull` | download updates from the pmemo_server


# Preference

name | default | description
-- | -- | --
out_dir | `$HOME/.pmemo` | specifies the directory where Pmemo saves memos
memo_pref.max_title_length | 30 | sets the maximum length of a memo title
editor_pref.prompt_spaces | 4 | defines the number of spaces used for line numbering in the editor
editor_pref.style_name | "github-dark" | sets the style of the editor
editor_pref.indentation_spaces | 4 | sets the number of spaces for indentation (tab size)
extensions_pref.openai_pref.api_key | None | The OpenAI API uses API keys for authentication
extensions_pref.openai_pref.model | "gpt-3.5-turbo" | ID of the model to use
extensions_pref.openai_pref.max_tokens | 16 | the maximum number of tokens to generate in the completion
extensions_pref.openai_pref.temperature | 0 | what sampling temperature to use, between 0 and 2
extensions_pref.openai_pref.n | 1 | how many completions to generate for each prompt
extensions_pref.openai_pref.key_binding | ctrl-O | post the selected range as a request to OpenAI
extensions_pref.template_pref.template_dir | `$HOME/.templates` | specifies the directory where templates in memos save
extensions_pref.template_pref.key_binding | ctrl-T | save the selected range as a template
api_pref.encryption_key | Fernet.generate_key | a key used for encryption
api_pref.user_token | None | the token used for user login
api_pref.user_refresh_token | None | the token used for refreshing the token



> [!NOTE]
> To enable ChatGPT functionality, make sure to set your OpenAI API key as an environment variable or preference.


> [!TIP]
> If you are pulling from a different terminal, you need to have the same encryption key.


# Versioning
This repo uses [Semantic Versioning](https://semver.org/).

# License
**pmemo** is released under the MIT License. See [LICENSE](/LICENSE) for additional details.
