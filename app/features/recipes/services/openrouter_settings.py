"""Configuration shared by OpenRouter adapters."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OpenRouterSettings:
    api_key: str
    base_url: str
    text_model: str
    image_model: str

    @classmethod
    def from_environment(cls) -> "OpenRouterSettings":
        return cls(
            api_key=os.environ.get("OPENROUTER_API_KEY", "").strip(),
            base_url=os.environ.get(
                "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
            ).rstrip("/"),
            text_model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            image_model=os.environ.get(
                "OPENROUTER_IMAGE_MODEL", "openai/gpt-image-2"
            ),
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
