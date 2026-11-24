"""Small HTTP client for OpenRouter JSON endpoints."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from .openrouter_settings import OpenRouterSettings


class OpenRouterClientError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(self, settings: OpenRouterSettings) -> None:
        self.settings = settings

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.settings.base_url}/{path.lstrip('/')}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            json.JSONDecodeError,
        ) as error:
            raise OpenRouterClientError("L’appel OpenRouter a échoué.") from error

        if not isinstance(parsed, dict):
            raise OpenRouterClientError("La réponse OpenRouter est invalide.")
        return parsed
