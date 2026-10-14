"""
Production-grade Ollama LLM client.
"""

from __future__ import annotations

from ollama import Client

from configs.logging import get_logger
from configs.settings import settings
from src.core.exceptions import LLMError

logger = get_logger(__name__)


class OllamaClient:
    """
    Wrapper around Ollama Python client.
    """

    _client: Client | None = None

    def __init__(self) -> None:

        if OllamaClient._client is None:

            OllamaClient._client = Client(
                host=settings.OLLAMA_HOST,
            )

            logger.info(
                "Connected to Ollama: %s",
                settings.OLLAMA_HOST,
            )

        self.client = OllamaClient._client

    # ---------------------------------------------------------

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        """
        Generate response from Ollama.
        """

        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        try:

            response = self.client.chat(
                model=settings.LLM_MODEL,
                messages=messages,
                options={
                    "temperature": temperature,
                },
            )

            return response["message"]["content"]

        except Exception as e:

            raise LLMError(
                "Failed to generate LLM response."
            ) from e

    # ---------------------------------------------------------

    def health_check(self) -> bool:
        """
        Check whether the configured model is available.
        """

        try:

            models = self.client.list()

            model_names = {
                model["model"]
                for model in models["models"]
            }

            return settings.llm_model in model_names

        except Exception:

            return False