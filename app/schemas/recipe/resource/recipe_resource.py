"""Recipe representation exposed to the frontend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from app.models import Recipe

from app.models import MealTime


class MealTimeResource(BaseModel):
    slug: str
    label: str


class RecipeIngredientResource(BaseModel):
    id: int
    name: str
    quantity: float
    unit: str | None
    position: int


class RecipeStepResource(BaseModel):
    id: int
    instruction: str
    position: int


class RecipeResource(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    description: str | None
    preparationTime: int
    cookingTime: int
    imageUrl: str | None
    imageGenerationStatus: str
    mealTimes: list[MealTimeResource]
    ingredients: list[RecipeIngredientResource]
    steps: list[RecipeStepResource]

    @classmethod
    def from_recipe(cls, recipe: Recipe, *, image_url: str | None) -> "RecipeResource":
        return cls(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            preparationTime=recipe.preparation_time,
            cookingTime=recipe.cooking_time,
            imageUrl=image_url,
            imageGenerationStatus=recipe.image_generation_status,
            mealTimes=[
                MealTimeResource(slug=slug, label=MealTime(slug).label)
                for slug in recipe.meal_times
            ],
            ingredients=[
                RecipeIngredientResource(
                    id=ingredient.id,
                    name=ingredient.name,
                    quantity=float(ingredient.quantity),
                    unit=ingredient.unit,
                    position=ingredient.position,
                )
                for ingredient in recipe.ingredients.all()
            ],
            steps=[
                RecipeStepResource(
                    id=step.id,
                    instruction=step.instruction,
                    position=step.position,
                )
                for step in recipe.steps.all()
            ],
        )
