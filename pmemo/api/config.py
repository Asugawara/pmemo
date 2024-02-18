import os

from pydantic import BaseModel


class APIConfig(BaseModel, frozen=True):
    domain: str = "https://pmemo.asugawara.com"
    version: str = "v1"

    @property
    def signup(self) -> str:
        return os.path.join(self.domain, self.version, "signup")

    @property
    def login(self) -> str:
        return os.path.join(self.domain, self.version, "login")

    @property
    def refresh_token(self) -> str:
        return os.path.join(self.domain, self.version, "refresh_token")

    @property
    def password_update(self) -> str:
        return os.path.join(self.domain, self.version, "password_update")

    @property
    def memos(self) -> str:
        return os.path.join(self.domain, self.version, "memos")


class Tokens(BaseModel, frozen=True):
    token: str = ""
    refresh_token: str = ""
