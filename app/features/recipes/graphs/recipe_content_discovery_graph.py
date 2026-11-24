from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from ..contexts.recipe_content_discovery_context import RecipeContentDiscoveryContext
from ..nodes.generate_image_node import generate_image
from ..nodes.generate_recipe_node import generate_recipe
from ..states.recipe_content_discovery_state import RecipeContentDiscoveryState


recipe_content_discovery_graph = (
    StateGraph(
        RecipeContentDiscoveryState,
        context_schema=RecipeContentDiscoveryContext,
    )
    .add_node("generate_recipe", generate_recipe)
    .add_node("generate_image", generate_image)
    .add_edge(START, "generate_recipe")
    .add_edge("generate_recipe", "generate_image")
    .add_edge("generate_image", END)
    .compile()
)
