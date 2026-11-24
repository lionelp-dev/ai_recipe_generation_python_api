from __future__ import annotations

from langgraph.runtime import Runtime

from ..contexts.recipe_content_discovery_context import RecipeContentDiscoveryContext
from ..states.recipe_content_discovery_state import RecipeContentDiscoveryState


def generate_image(
    state: RecipeContentDiscoveryState, runtime: Runtime[RecipeContentDiscoveryContext]
) -> dict[str, object]:
    recipe = state.get("generated_recipe")

    if recipe is None:
        return {"image_data_url": None, "image_generation_failed": True}

    image_data_url = runtime.context.image_generator.generate(recipe.name)

    return {
        "image_data_url": image_data_url,
        "image_generation_failed": image_data_url is None,
    }
