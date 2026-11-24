"""OpenRouter adapter for generated recipe images."""

from __future__ import annotations

import base64
import binascii
import logging
from typing import Any

from .openrouter_client import OpenRouterClient, OpenRouterClientError
from .openrouter_settings import OpenRouterSettings

MAX_GENERATED_IMAGE_SIZE = 5 * 1024 * 1024

logger = logging.getLogger(__name__)


class OpenRouterRecipeImageGenerator:
    def __init__(self, settings: OpenRouterSettings, client: OpenRouterClient) -> None:
        self.settings = settings
        self.client = client

    def generate(self, recipe_name: str) -> str | None:
        if not self.settings.is_configured:
            logger.warning(
                "Image generation skipped because OpenRouter is not configured "
                "(recipe_name=%r, image_model=%s)",
                recipe_name,
                self.settings.image_model,
            )
            return None

        try:
            payload = self.client.post_json(
                "images/generations",
                _image_request(recipe_name, self.settings.image_model),
            )
            image_data_url = _image_data_url(payload)
            if image_data_url is None:
                logger.warning(
                    "OpenRouter image response did not contain valid image data "
                    "(recipe_name=%r, image_model=%s)",
                    recipe_name,
                    self.settings.image_model,
                )
            return image_data_url
        except (OpenRouterClientError, ValueError, TypeError, binascii.Error) as error:
            logger.exception(
                "OpenRouter image generation failed "
                "(recipe_name=%r, image_model=%s, http_status=%s)",
                recipe_name,
                self.settings.image_model,
                getattr(error.__cause__, "code", None),
            )
            return None


def _image_request(recipe_name: str, image_model: str) -> dict[str, Any]:
    return {
        "model": image_model,
        "prompt": (
            f"Professional food photography of {recipe_name}, appetizing, well-lit, "
            "realistic, no text or watermark"
        ),
        "n": 1,
        "size": "1024x640",
        "quality": "low",
        "output_format": "jpeg",
    }


def _image_data_url(payload: dict[str, Any]) -> str | None:
    data = payload.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        return None

    encoded = data[0].get("b64_json")
    if not isinstance(encoded, str):
        return None

    content = base64.b64decode(encoded, validate=True)
    if not content or len(content) > MAX_GENERATED_IMAGE_SIZE:
        return None
    return f"data:image/jpeg;base64,{encoded}"
