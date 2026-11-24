from __future__ import annotations

from typing import TypedDict


class RecipeNameRequest(TypedDict):
    prompt: str
    required_meal_time_slug: str


class RecipeNameResult(RecipeNameRequest):
    name: str


class RecipeNameGenerationState(TypedDict, total=False):
    pending_name_requests: list[RecipeNameRequest]
    generated_name_results: list[RecipeNameResult]
    accepted_name_results: list[RecipeNameResult]
    excluded_names: list[str]
