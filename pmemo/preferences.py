from enum import Enum
from pathlib import Path
from typing import Optional

from prompt_toolkit.keys import Keys
from pydantic import BaseModel, PositiveInt


# ref: https://github.com/pygments/pygments/blob/c3e1371fceb104b69c613a014d0b2124f8d0fe1b/pygments/styles/__init__.py#L16
class PygmentsStyles(str, Enum):
    default = "default"
    emacs = "emacs"
    friendly = "friendly"
    friendly_grayscale = "friendly_grayscale"
    colorful = "colorful"
    autumn = "autumn"
    murphy = "murphy"
    manni = "manni"
    material = "material"
    monokai = "monokai"
    perldoc = "perldoc"
    pastie = "pastie"
    borland = "borland"
    trac = "trac"
    native = "native"
    fruity = "fruity"
    bw = "bw"
    vim = "vim"
    vs = "vs"
    tango = "tango"
    rrt = "rrt"
    xcode = "xcode"
    igor = "igor"
    paraiso_light = "paraiso-light"
    paraiso_dark = "paraiso-dark"
    lovelace = "lovelace"
    algol = "algol"
    algol_nu = "algol_nu"
    arduino = "arduino"
    rainbow_dash = "rainbow_dash"
    abap = "abap"
    solarized_dark = "solarized-dark"
    solarized_light = "solarized-light"
    sas = "sas"
    staroffice = "staroffice"
    stata = "stata"
    stata_light = "stata-light"
    stata_dark = "stata-dark"
    inkpot = "inkpot"
    zenburn = "zenburn"
    gruvbox_dark = "gruvbox-dark"
    gruvbox_light = "gruvbox-light"
    dracula = "dracula"
    one_dark = "one-dark"
    lilypond = "lilypond"
    nord = "nord"
    nord_darker = "nord-darker"
    github_dark = "github-dark"


class EditorPreference(BaseModel, frozen=True):
    prompt_spaces: PositiveInt = 4
    style_name: PygmentsStyles = PygmentsStyles.github_dark
    indentation_spaces: PositiveInt = 4


class MemoPreference(BaseModel, frozen=True):
    max_title_length: PositiveInt = 30


# ref: https://platform.openai.com/docs/api-reference/completions/create
class OpenAiPreference(BaseModel, frozen=True):
    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 16
    temperature: int = 0
    n: int = 1
    key_map: Keys = Keys.ControlO


PREFERENCE_FILE_PATH = Path(__file__).parent / ".preference"


class PmemoPreference(BaseModel, frozen=True):
    out_dir: Path = Path.home() / ".pmemo"
    memo_preference: MemoPreference = MemoPreference()
    editor_preference: EditorPreference = EditorPreference()
    openai_preference: OpenAiPreference = OpenAiPreference()

    def write(self):
        PREFERENCE_FILE_PATH.write_text(self.json())
