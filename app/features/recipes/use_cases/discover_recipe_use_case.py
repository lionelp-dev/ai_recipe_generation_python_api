from __future__ import annotations

import logging
from typing import Any

from ..contexts.recipe_content_discovery_context import RecipeContentDiscoveryContext
from ..contexts.recipe_name_generation_context import RecipeNameGenerationContext
from ..graphs.recipe_content_discovery_graph import recipe_content_discovery_graph
from ..graphs.recipe_name_generation_graph import recipe_name_generation_graph
from app.repositories.recipe_repository import RecipeRepository
from ..services.openrouter_chat_model_factory import OpenRouterChatModelFactory
from ..services.openrouter_client import OpenRouterClient
from ..services.openrouter_recipe_generator import OpenRouterRecipeTextGenerator
from ..services.openrouter_recipe_image_generator import OpenRouterRecipeImageGenerator
from ..services.openrouter_settings import OpenRouterSettings
from ..states.recipe_content_discovery_state import RecipeContentDiscoveryState
from ..states.recipe_name_generation_state import RecipeNameRequest, RecipeNameResult
from app.schemas import DiscoveredRecipeResource, RecipeData

TARGET_RECIPE_COUNT = 1
MAX_GENERATION_CONCURRENCY = 20

logger = logging.getLogger(__name__)


class DiscoverRecipeUseCase:
    def __init__(
        self,
        recipe_generator: OpenRouterRecipeTextGenerator,
        image_generator: OpenRouterRecipeImageGenerator,
        recipe_repository: RecipeRepository,
    ) -> None:
        self.recipe_generator = recipe_generator
        self.image_generator = image_generator
        self.recipe_repository = recipe_repository

    def is_configured(self) -> bool:
        return self.recipe_generator.is_configured()

    def execute(
        self,
        prompt: str,
        requested_meal_times: list[str],
        available_meal_times: list[str],
        *,
        batch_id: str | None = None,
    ) -> dict[str, Any]:
        recipe_name_requests = self._build_recipe_name_requests(
            prompt,
            requested_meal_times,
            available_meal_times,
        )
        recipe_name_generation_result = recipe_name_generation_graph.invoke(
            {
                "pending_name_requests": recipe_name_requests,
                "generated_name_results": [],
                "accepted_name_results": [],
                "excluded_names": [],
            },
            context=RecipeNameGenerationContext(
                recipe_generator=self.recipe_generator,
                recipes=self.recipe_repository,
            ),
        )
        named_recipe_candidates = recipe_name_generation_result.get(
            "accepted_name_results", []
        )

        if len(named_recipe_candidates) != TARGET_RECIPE_COUNT:
            raise ValueError("Le lot de noms de recettes est incomplet.")

        recipe_content_inputs: list[RecipeContentDiscoveryState] = [
            {
                "prompt": candidate["prompt"],
                "required_meal_time_slug": candidate["required_meal_time_slug"],
                "generated_recipe_name": candidate["name"],
                "generated_recipe": None,
                "image_data_url": None,
                "image_generation_failed": False,
            }
            for candidate in named_recipe_candidates
        ]
        recipe_content_generation_results = recipe_content_discovery_graph.batch(
            recipe_content_inputs,
            config={"max_concurrency": MAX_GENERATION_CONCURRENCY},
            context=RecipeContentDiscoveryContext(
                recipe_generator=self.recipe_generator,
                image_generator=self.image_generator,
            ),
            return_exceptions=True,
        )

        discovered_recipes = self._collect_discovered_recipes(
            named_recipe_candidates,
            recipe_content_generation_results,
            batch_id=batch_id,
        )

        failed_recipe_count = TARGET_RECIPE_COUNT - len(discovered_recipes)

        logger.info(
            "Recipe discovery batch completed "
            "(batch_id=%s, generated_recipe_count=%s, failed_recipe_count=%s, target_recipe_count=%s)",
            batch_id,
            len(discovered_recipes),
            failed_recipe_count,
            TARGET_RECIPE_COUNT,
        )
        return {
            "recipes": discovered_recipes,
            "failedRecipeCount": failed_recipe_count,
        }

    @staticmethod
    def _build_recipe_name_requests(
        prompt: str,
        requested_meal_times: list[str],
        available_meal_times: list[str],
    ) -> list[RecipeNameRequest]:
        target_meal_times = requested_meal_times or available_meal_times
        if not target_meal_times:
            raise ValueError("Le catalogue des moments de repas est vide.")

        recipe_name_requests: list[RecipeNameRequest] = []
        for index in range(TARGET_RECIPE_COUNT):
            meal_time = target_meal_times[index % len(target_meal_times)]
            recipe_name_requests.append(
                {
                    "prompt": (
                        f"{prompt}\n\nContrainte obligatoire — moment de repas : "
                        f"{meal_time}. La recette doit réellement et uniquement "
                        "convenir à ce moment."
                    ),
                    "required_meal_time_slug": meal_time,
                }
            )
        return recipe_name_requests

    @staticmethod
    def _collect_discovered_recipes(
        named_recipe_candidates: list[RecipeNameResult],
        recipe_content_generation_results: list[dict[str, object] | Exception],
        *,
        batch_id: str | None,
    ) -> list[dict[str, Any]]:
        discovered_recipes: list[dict[str, Any]] = []
        for index, generation_result in enumerate(recipe_content_generation_results):
            recipe_name = named_recipe_candidates[index]["name"]
            if isinstance(generation_result, Exception):
                DiscoverRecipeUseCase._log_content_generation_exception(
                    generation_result,
                    recipe_name=recipe_name,
                    index=index,
                    batch_id=batch_id,
                )
                continue

            generated_recipe = generation_result.get("generated_recipe")
            if not isinstance(generated_recipe, RecipeData):
                DiscoverRecipeUseCase._log_missing_recipe(
                    recipe_name,
                    index=index,
                    batch_id=batch_id,
                )
                continue

            if generation_result.get("image_generation_failed"):
                DiscoverRecipeUseCase._log_missing_image(
                    generated_recipe.name,
                    index=index,
                    batch_id=batch_id,
                )
                continue

            discovered_recipes.append(
                DiscoveredRecipeResource.from_data(
                    generated_recipe,
                    image_data_url=generation_result.get("image_data_url"),
                    image_generation_failed=bool(
                        generation_result.get("image_generation_failed")
                    ),
                ).model_dump(mode="json")
            )
        return discovered_recipes

    @staticmethod
    def _log_content_generation_exception(
        error: Exception,
        *,
        recipe_name: str,
        index: int,
        batch_id: str | None,
    ) -> None:
        logger.error(
            "Recipe discovery candidate failed "
            "(batch_id=%s, candidate_index=%s, recipe_name=%r, stage=%s)",
            batch_id,
            index,
            recipe_name,
            "recipe_or_image_generation",
            exc_info=(type(error), error, error.__traceback__),
        )

    @staticmethod
    def _log_missing_recipe(
        recipe_name: str, *, index: int, batch_id: str | None
    ) -> None:
        logger.warning(
            "Recipe discovery candidate produced no valid recipe "
            "(batch_id=%s, candidate_index=%s, recipe_name=%r, stage=%s)",
            batch_id,
            index,
            recipe_name,
            "recipe_generation",
        )

    @staticmethod
    def _log_missing_image(
        recipe_name: str, *, index: int, batch_id: str | None
    ) -> None:
        logger.warning(
            "Recipe discovery candidate discarded because image generation failed "
            "(batch_id=%s, candidate_index=%s, recipe_name=%r, stage=%s)",
            batch_id,
            index,
            recipe_name,
            "image_generation",
        )


def create_discover_recipe_use_case() -> DiscoverRecipeUseCase:
    settings = OpenRouterSettings.from_environment()
    return DiscoverRecipeUseCase(
        recipe_generator=OpenRouterRecipeTextGenerator(
            OpenRouterChatModelFactory(settings)
        ),
        image_generator=OpenRouterRecipeImageGenerator(
            settings,
            OpenRouterClient(settings),
        ),
        recipe_repository=RecipeRepository(),
    )
