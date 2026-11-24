from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from ..contexts.recipe_name_generation_context import RecipeNameGenerationContext
from ..nodes.check_recipe_name_duplicates_node import check_recipe_name_duplicates
from ..nodes.generate_recipe_names_node import generate_recipe_names
from ..states.recipe_name_generation_state import RecipeNameGenerationState


def _names_complete(state: RecipeNameGenerationState) -> str:
    return END if not state.get("pending_name_requests") else "generate_recipe_names"


recipe_name_generation_graph = (
    StateGraph(
        RecipeNameGenerationState,
        context_schema=RecipeNameGenerationContext,
    )
    .add_node("generate_recipe_names", generate_recipe_names)
    .add_node("check_recipe_name_duplicates", check_recipe_name_duplicates)
    .add_edge(START, "generate_recipe_names")
    .add_edge("generate_recipe_names", "check_recipe_name_duplicates")
    .add_conditional_edges("check_recipe_name_duplicates", _names_complete)
    .compile()
)
