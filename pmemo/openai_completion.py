from typing import Optional

import openai


class OpenAiCompletion:
    """
    Wrapper class for OpenAI text completion using the OpenAI API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        **kwargs,
    ) -> None:
        """
        Initialize the OpenAiCompletion instance.

        Args:
            api_key (Optional[str]): The API key for accessing the OpenAI API.
            model (str): The model to use for text completion (default: "gpt-3.5-turbo").
            **kwargs: Additional keyword arguments to be passed to the OpenAI API.
        """
        self._api_key = api_key
        self._model = model
        self._kwargs = kwargs

    def request_chatgpt(self, prompt: str) -> str:
        """
        Request text completion from OpenAI Model based on the provided prompt.

        Args:
            prompt (str): The prompt to generate a completion for.

        Returns:
            str: The generated completion text.
        """
        if not prompt:
            return ""
        if openai.api_key is None and self._api_key is None:
            raise RuntimeError("OpenAI API key is missing or not provided")
        openai.api_key = openai.api_key or self._api_key
        completion = openai.ChatCompletion.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            **self._kwargs,
        )
        return completion.choices[0].message.content
