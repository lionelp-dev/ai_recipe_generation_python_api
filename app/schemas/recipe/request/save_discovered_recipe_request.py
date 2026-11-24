"""Validation schema for persisting a discovered recipe."""

from pydantic import BaseModel, Field, StrictStr

from .recipe_request import RecipeRequest


class SaveDiscoveredRecipeRequest(BaseModel):
    """Outer payload for persisting one recipe proposed by discovery."""

    recipe: RecipeRequest
    image_data_url: StrictStr | None = Field(default=None, alias="imageDataUrl")
