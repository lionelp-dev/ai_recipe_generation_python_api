from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile

from app.features.recipes.services.image_storage_service import (
    delete_recipe_image,
    store_data_url,
    store_uploaded_image,
)


class RecipeImageRepository:
    def store_uploaded(self, upload: UploadedFile) -> str:
        return store_uploaded_image(upload)

    def store_data_url(self, data_url: str) -> str:
        return store_data_url(data_url)

    def delete(self, image_key: str) -> None:
        delete_recipe_image(image_key)
