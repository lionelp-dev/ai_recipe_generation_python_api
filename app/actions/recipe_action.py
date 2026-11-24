from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from app.models import Recipe
from app.repositories.recipe_image_repository import RecipeImageRepository
from app.repositories.recipe_repository import RecipeRepository
from app.schemas import RecipeData


def create_recipe(data: RecipeData, uploaded_image: UploadedFile | None) -> Recipe:
    images = RecipeImageRepository()
    image_key = images.store_uploaded(uploaded_image) if uploaded_image else None
    return _persist_recipe(data, image_key, images)


def create_discovered_recipe(data: RecipeData, image_data_url: str | None) -> int:
    images = RecipeImageRepository()
    image_key = images.store_data_url(image_data_url) if image_data_url else None
    return _persist_recipe(data, image_key, images).id


def update_recipe(
    recipe: Recipe,
    data: RecipeData,
    uploaded_image: UploadedFile | None,
    remove_image: bool,
) -> None:
    recipes = RecipeRepository()
    images = RecipeImageRepository()
    previous_image_key = recipe.image_key
    image_key = previous_image_key
    image_status = recipe.image_generation_status
    new_image_key: str | None = None

    try:
        if uploaded_image:
            new_image_key = images.store_uploaded(uploaded_image)
            image_key = new_image_key
            image_status = Recipe.ImageGenerationStatus.READY
        elif remove_image:
            image_key = None
            image_status = Recipe.ImageGenerationStatus.NOT_REQUESTED

        with transaction.atomic():
            recipes.replace(recipe, data, image_status, image_key)
            if previous_image_key and previous_image_key != image_key:
                transaction.on_commit(
                    lambda image_key=previous_image_key: images.delete(image_key)
                )
    except Exception:
        if new_image_key:
            images.delete(new_image_key)
        raise


def _persist_recipe(
    data: RecipeData,
    image_key: str | None,
    images: RecipeImageRepository,
) -> Recipe:
    try:
        image_status = (
            Recipe.ImageGenerationStatus.READY
            if image_key
            else Recipe.ImageGenerationStatus.NOT_REQUESTED
        )
        with transaction.atomic():
            return RecipeRepository().create(data, image_status, image_key)
    except Exception:
        if image_key:
            images.delete(image_key)
        raise
