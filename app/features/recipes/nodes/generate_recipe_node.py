from __future__ import annotations

from langgraph.runtime import Runtime

from ..contexts.recipe_content_discovery_context import RecipeContentDiscoveryContext
from ..states.recipe_content_discovery_state import RecipeContentDiscoveryState


def generate_recipe(
    state: RecipeContentDiscoveryState, runtime: Runtime[RecipeContentDiscoveryContext]
) -> dict[str, object]:
    prompt = state.get("prompt")
    recipe_name = state.get("generated_recipe_name")
    meal_time = state.get("required_meal_time_slug")

    if not prompt or not recipe_name or not meal_time:
        raise ValueError("La recette ne possède pas les données de génération requises.")

    recipe = runtime.context.recipe_generator.generate_recipe(
        prompt, recipe_name, [meal_time]
    )

    return {"generated_recipe": recipe}
