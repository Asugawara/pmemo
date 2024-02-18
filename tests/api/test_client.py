import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from pmemo.api.client import APIClient


@pytest.fixture
def api_client():
    tokens = MagicMock()
    encryption_key = b"wQCp-8OppuyV3nKM4D0ugNJ1zmalbksJZZAYuydI_IA="
    return APIClient(tokens, encryption_key)


def test_store_memo(api_client):
    mock_post = MagicMock()
    mock_post.status_code = 200
    with patch("requests.post", return_value=mock_post) as mock_requests_post:
        file_name = b"test_file.txt"
        content = b"This is a test memo"
        api_client.store_memo(file_name, content)
        mock_requests_post.assert_called_once()


def test_store_memo_failed(api_client):
    mock_post = MagicMock()
    mock_post.status_code = 500
    with patch("requests.post", return_value=mock_post) as mock_requests_post:
        file_name = b"test_file.txt"
        content = b"This is a test memo"
        api_client.store_memo(file_name, content)
        mock_requests_post.assert_called_once()


def test_get_memos(api_client):
    mock_get = MagicMock()
    mock_get.status_code = requests.codes.ok
    mock_get.json.return_value = [
        {"content": api_client._fernet.encrypt(b"memo1").decode("utf-8")},
        {"content": api_client._fernet.encrypt(b"memo2").decode("utf-8")},
    ]
    with patch("requests.get", return_value=mock_get) as mock_requests_get:
        decrypted_contents = api_client.get_memos()

        mock_requests_get.assert_called_once_with(
            api_client._config.memos,
            headers={"Authorization": f"Bearer {api_client._tokens.token}"},
        )

        assert decrypted_contents == ["memo1", "memo2"]


def test_get_memos_failed(api_client):
    mock_get = MagicMock()
    mock_get.status_code = 500
    with patch("requests.get", return_value=mock_get) as mock_requests_get:
        decrypted_contents = api_client.get_memos()
        mock_requests_get.assert_called_once_with(
            api_client._config.memos,
            headers={"Authorization": f"Bearer {api_client._tokens.token}"},
        )
        assert decrypted_contents == []
