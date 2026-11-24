from __future__ import annotations

from app.models import Recipe, RecipeIngredient, RecipeStep
from app.schemas import RecipeData


class RecipeRepository:
    def find_existing_recipe_names(self, names: list[str]) -> list[str]:
        # Discovery currently has no persistent recipe catalogue. Keeping this
        # boundary lets the graph still reject duplicates generated in one batch
        # without requiring the recipe table to exist.
        return []

    def create(
        self, data: RecipeData, image_status: str, image_key: str | None = None
    ) -> Recipe:
        recipe = Recipe.objects.create(
            name=data.name,
            description=data.description,
            preparation_time=data.preparation_time,
            cooking_time=data.cooking_time,
            image_key=image_key,
            image_generation_status=image_status,
            meal_times=data.meal_times,
        )
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(recipe=recipe, position=index, **ingredient.model_dump())
                for index, ingredient in enumerate(data.ingredients)
            ]
        )
        RecipeStep.objects.bulk_create(
            [
                RecipeStep(recipe=recipe, position=index, **step.model_dump())
                for index, step in enumerate(data.steps)
            ]
        )
        return recipe

    def replace(
        self, recipe: Recipe, data: RecipeData, image_status: str, image_key: str | None
    ) -> None:
        recipe.name = data.name
        recipe.description = data.description
        recipe.preparation_time = data.preparation_time
        recipe.cooking_time = data.cooking_time
        recipe.image_key = image_key
        recipe.image_generation_status = image_status
        recipe.meal_times = data.meal_times
        recipe.save()
        recipe.ingredients.all().delete()
        recipe.steps.all().delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(recipe=recipe, position=index, **ingredient.model_dump())
                for index, ingredient in enumerate(data.ingredients)
            ]
        )
        RecipeStep.objects.bulk_create(
            [
                RecipeStep(recipe=recipe, position=index, **step.model_dump())
                for index, step in enumerate(data.steps)
            ]
        )
