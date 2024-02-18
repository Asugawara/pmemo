import json

import requests
from cryptography.fernet import Fernet
from logzero import logger

from pmemo.api.config import APIConfig, Tokens


class APIClient:
    def __init__(self, tokens: Tokens, encryption_key: bytes) -> None:
        self._config = APIConfig()
        self._tokens = tokens
        self._fernet = Fernet(encryption_key)

    def store_memo(self, file_name: bytes, content: bytes) -> None:
        # Note: Identical file names should yield same encryption
        IV = b"\xb3\x03\xbdVn\xeejKH\xc4\x0c\x83\xa7\xba_\x8e"
        encrypted_file_name = self._fernet._encrypt_from_parts(file_name, 0, IV).decode(
            "utf-8"
        )
        encrypted_content = self._fernet.encrypt(content).decode("utf-8")
        res = requests.post(
            self._config.memos,
            headers={"Authorization": f"Bearer {self._tokens.token}"},
            data=json.dumps(
                dict(file_name=encrypted_file_name, content=encrypted_content)
            ),
        )
        if res.status_code == requests.codes.ok:
            logger.info("Memo stored successfully: %s", file_name.decode("utf-8"))
        else:
            logger.error("Failed to store memo")
            if self._tokens.token:
                logger.error("Maybe login again to refresh the token")

    def get_memos(self) -> list[str]:
        res = requests.get(
            self._config.memos,
            headers={"Authorization": f"Bearer {self._tokens.token}"},
        )
        if res.status_code != requests.codes.ok:
            logger.error("Failed to get memos")
            if self._tokens.token:
                logger.error("Maybe login again to refresh the token")
            return []
        decrypted_contents = []
        for memo in res.json():
            decrypted_contents.append(
                self._fernet.decrypt(memo["content"].encode()).decode("utf-8")
            )
        return decrypted_contents
