from __future__ import annotations

from dataclasses import dataclass

from app.repositories.recipe_repository import RecipeRepository
from ..services.openrouter_recipe_generator import OpenRouterRecipeTextGenerator


@dataclass(frozen=True, slots=True)
class RecipeNameGenerationContext:
    recipe_generator: OpenRouterRecipeTextGenerator
    recipes: RecipeRepository
