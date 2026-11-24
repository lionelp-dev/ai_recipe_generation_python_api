"""LangChain chat-model construction for OpenRouter."""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from .openrouter_settings import OpenRouterSettings


class OpenRouterChatModelFactory:
    """Create text models from shared OpenRouter settings."""

    def __init__(self, settings: OpenRouterSettings) -> None:
        self.settings = settings

    def is_configured(self) -> bool:
        return self.settings.is_configured

    def create_text_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self.settings.text_model,
            api_key=SecretStr(self.settings.api_key),
            base_url=self.settings.base_url,
            temperature=0.8,
            timeout=60,
            max_retries=0,
        )
