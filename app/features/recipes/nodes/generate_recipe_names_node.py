from __future__ import annotations

from langgraph.runtime import Runtime

from ..contexts.recipe_name_generation_context import RecipeNameGenerationContext
from ..states.recipe_name_generation_state import RecipeNameGenerationState


def generate_recipe_names(
    state: RecipeNameGenerationState, runtime: Runtime[RecipeNameGenerationContext]
) -> dict[str, object]:
    requests = state.get("pending_name_requests", [])
    if not requests:
        raise ValueError("Aucun nom de recette ne manque dans le lot.")
    names = runtime.context.recipe_generator.generate_names(
        requests, state.get("excluded_names", [])
    )
    if len(names) != len(requests):
        raise ValueError("La génération de noms de recettes est incomplète.")
    return {
        "generated_name_results": [
            {**request, "name": names[index]}
            for index, request in enumerate(requests)
        ]
    }
