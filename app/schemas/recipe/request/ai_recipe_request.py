from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..data import RecipeData
from .ai_ingredient_request import GeneratedIngredientRequest
from .ai_recipe_step_request import GeneratedRecipeStepRequest


class GeneratedRecipeRequest(BaseModel):
    """Structured but untrusted recipe payload returned by OpenRouter."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    preparationTime: int = Field(ge=0)
    cookingTime: int = Field(ge=0)
    ingredients: list[GeneratedIngredientRequest]
    steps: list[GeneratedRecipeStepRequest] = Field(min_length=1)
    mealTimes: list[str] = Field(min_length=1)

    def to_data(self, *, known_meal_times: list[str]) -> RecipeData:
        return RecipeData.model_validate(
            {
                "name": self.name,
                "description": self.description,
                "preparation_time": self.preparationTime,
                "cooking_time": self.cookingTime,
                "ingredients": [
                    ingredient.model_dump() for ingredient in self.ingredients
                ],
                "steps": [step.model_dump() for step in self.steps],
                "meal_times": self.mealTimes,
            },
            context={"generated": True, "known_meal_times": known_meal_times},
        )
