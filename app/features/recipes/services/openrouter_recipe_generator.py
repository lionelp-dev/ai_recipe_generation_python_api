"""OpenRouter adapter for recipe-name and recipe-content generation."""

from __future__ import annotations

from typing import Annotated, cast

from pydantic import BaseModel, Field, create_model

from app.schemas import GeneratedRecipeRequest, RecipeData

from ..states.recipe_name_generation_state import RecipeNameRequest
from .openrouter_chat_model_factory import OpenRouterChatModelFactory

RECIPE_NAMES_SYSTEM_PROMPT = (
    "Tu es un chef cuisinier. Propose exactement un nom de recette réaliste par "
    "demande, dans le même ordre. Tous les noms doivent être distincts, variés et "
    "distincts des noms exclus."
)


class OpenRouterRecipeTextGenerator:
    def __init__(self, model_factory: OpenRouterChatModelFactory) -> None:
        self.model_factory = model_factory

    def is_configured(self) -> bool:
        return self.model_factory.is_configured()

    def generate_names(
        self, requests: list[RecipeNameRequest], excluded_names: list[str]
    ) -> list[str]:
        if not requests:
            return []

        model = self.model_factory.create_text_model().with_structured_output(
            _generated_recipe_names_schema(len(requests)),
            method="json_schema",
            strict=True,
        )
        generated = model.invoke(
            [
                ("system", RECIPE_NAMES_SYSTEM_PROMPT),
                ("human", _recipe_names_prompt(requests, excluded_names)),
            ]
        )
        names = [name.strip() for name in generated.names]
        if len(names) != len(requests) or any(not name for name in names):
            raise ValueError(
                "Le nombre de noms générés est invalide "
                f"(attendu={len(requests)}, reçu={len(names)})."
            )
        return names

    def generate_recipe(
        self, prompt: str, recipe_name: str, allowed_meal_time_slugs: list[str]
    ) -> RecipeData:
        model = self.model_factory.create_text_model().with_structured_output(
            GeneratedRecipeRequest,
            method="json_schema",
            strict=True,
        )
        generated = cast(
            GeneratedRecipeRequest,
            model.invoke(
                [
                    ("system", _recipe_system_prompt(allowed_meal_time_slugs)),
                    ("human", _recipe_prompt(prompt, recipe_name)),
                ]
            ),
        )
        recipe = generated.to_data(known_meal_times=allowed_meal_time_slugs)
        if recipe.name != recipe_name:
            raise ValueError("Le nom généré ne correspond pas au nom demandé.")
        return recipe


def _recipe_names_prompt(
    requests: list[RecipeNameRequest], excluded_names: list[str]
) -> str:
    formatted_requests = "\n\n".join(
        f"{index + 1}. {request['prompt']}" for index, request in enumerate(requests)
    )
    return (
        f"Demandes :\n{formatted_requests}\n\n"
        f"Noms exclus : {', '.join(excluded_names) or 'aucun'}"
    )


def _recipe_system_prompt(allowed_meal_time_slugs: list[str]) -> str:
    return (
        "Tu es un chef cuisinier expert. Génère des recettes réalistes, variées et "
        "directement exploitables. Chaque recette doit avoir des quantités cohérentes, "
        "des durées en minutes, et au moins une étape claire. La recette doit contenir "
        "au moins un moment de repas autorisé et aucun autre. "
        f"Moments de repas autorisés : {', '.join(allowed_meal_time_slugs)}."
    )


def _recipe_prompt(prompt: str, recipe_name: str) -> str:
    return (
        f"Demande utilisateur : {prompt}\n\n"
        f"Génère la recette complète dont le nom doit être exactement : {recipe_name}."
    )


def _generated_recipe_names_schema(expected_name_count: int) -> type[BaseModel]:
    return create_model(
        "GeneratedRecipeNames",
        names=(
            list[Annotated[str, Field(min_length=1, max_length=160)]],
            Field(min_length=expected_name_count, max_length=expected_name_count),
        ),
    )
