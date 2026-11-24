from __future__ import annotations

from langgraph.runtime import Runtime

from ..contexts.recipe_name_generation_context import RecipeNameGenerationContext
from ..states.recipe_name_generation_state import RecipeNameGenerationState, RecipeNameRequest


def normalize_recipe_name(name: str) -> str:
    return " ".join(name.strip().split()).lower()


def check_recipe_name_duplicates(
    state: RecipeNameGenerationState, runtime: Runtime[RecipeNameGenerationContext]
) -> dict[str, object]:
    generated_name_results = state.get("generated_name_results", [])
    if not generated_name_results:
        raise ValueError("Aucun nom généré à vérifier.")
    existing = {
        normalize_recipe_name(name)
        for name in runtime.context.recipes.find_existing_recipe_names(
            [result["name"] for result in generated_name_results]
        )
    }
    accepted = list(state.get("accepted_name_results", []))
    accepted_names = {normalize_recipe_name(result["name"]) for result in accepted}
    pending: list[RecipeNameRequest] = []
    rejected: list[str] = []
    for result in generated_name_results:
        normalized = normalize_recipe_name(result["name"])
        if normalized in existing or normalized in accepted_names:
            pending.append(
                {
                    "prompt": result["prompt"],
                    "required_meal_time_slug": result["required_meal_time_slug"],
                }
            )
            rejected.append(result["name"])
            continue
        accepted.append(result)
        accepted_names.add(normalized)
    return {
        "accepted_name_results": accepted,
        "pending_name_requests": pending,
        "generated_name_results": [],
        "excluded_names": list(
            dict.fromkeys(
                [
                    *state.get("excluded_names", []),
                    *(result["name"] for result in accepted),
                    *rejected,
                ]
            )
        ),
    }
