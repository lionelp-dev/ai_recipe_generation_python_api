from __future__ import annotations

from dataclasses import dataclass

from ..services.openrouter_recipe_generator import OpenRouterRecipeTextGenerator
from ..services.openrouter_recipe_image_generator import OpenRouterRecipeImageGenerator


@dataclass(frozen=True, slots=True)
class RecipeContentDiscoveryContext:
    recipe_generator: OpenRouterRecipeTextGenerator
    image_generator: OpenRouterRecipeImageGenerator
