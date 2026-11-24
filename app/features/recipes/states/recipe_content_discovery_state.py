from __future__ import annotations

from typing import TypedDict

from app.schemas import RecipeData


class RecipeContentDiscoveryState(TypedDict, total=False):
    prompt: str
    required_meal_time_slug: str
    generated_recipe_name: str
    generated_recipe: RecipeData | None
    image_data_url: str | None
    image_generation_failed: bool
