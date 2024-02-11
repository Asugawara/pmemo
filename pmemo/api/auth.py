import json
from typing import Optional

import requests
from logzero import logger
from prompt_toolkit import prompt

from pmemo.api.config import APIConfig, Tokens


def input_email() -> str:
    return prompt("Email:")


def input_password() -> str:
    return prompt("Password:", is_password=True)


class APIAuthenticator:
    def __init__(self) -> None:
        self._config = APIConfig()

    def _input_user_info(self) -> tuple[str, str]:
        email = input_email()
        password = input_password()
        return email, password

    def signup(self) -> Tokens:
        email, password = self._input_user_info()
        res = requests.post(
            self._config.signup, data=json.dumps({"email": email, "password": password})
        )
        tokens = res.json()
        if res.status_code == requests.codes.ok:
            logger.info("Signup Success")
        else:
            logger.error("Signup Failed")
        return Tokens(
            token=tokens.get("idToken", ""),
            refresh_token=tokens.get("refreshToken", ""),
        )

    def _refresh_token(self, refresh_token: str) -> Tokens:
        res = requests.post(
            self._config.refresh_token,
            data=json.dumps({"refresh_token": refresh_token.strip('"')}),
        )
        tokens = res.json()
        if res.status_code == requests.codes.ok:
            logger.info("Refresh Token Success")
        else:
            logger.error("Refresh Token Failed")
        return Tokens(
            token=tokens.get("id_token", ""),
            refresh_token=tokens.get("refresh_token", refresh_token),
        )

    def login(self, refresh_token: Optional[str]) -> Tokens:
        if refresh_token is not None:
            return self._refresh_token(refresh_token)
        email, password = self._input_user_info()
        res = requests.post(
            self._config.login,
            data=json.dumps({"email": email, "password": password}),
        )
        tokens = res.json()
        if res.status_code == requests.codes.ok:
            logger.info("Login Success")
        else:
            logger.error("Login Failed")
        return Tokens(
            token=tokens.get("idToken", ""),
            refresh_token=tokens.get("refreshToken", ""),
        )
