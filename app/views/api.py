from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from app.api_serializers import DiscoverRecipesSerializer
from app.features.recipes.use_cases.discover_recipe_use_case import (
    create_discover_recipe_use_case,
)
from app.models import MealTime

logger = logging.getLogger(__name__)


@api_view(["POST"])
def discover_recipes_api(request: Request) -> Response:
    """Generate a transient batch of recipe suggestions from Discovery criteria."""

    serializer = DiscoverRecipesSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    payload = serializer.validated_data
    available_meal_times = list(MealTime.values)

    use_case = create_discover_recipe_use_case()
    if not use_case.is_configured():
        return Response(
            {"error": "Le mode Discovery n'est pas configuré."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    try:
        batch = use_case.execute(
            payload["prompt"],
            payload["selectedMealTimes"],
            available_meal_times,
        )
    except Exception:
        logger.exception("Recipe discovery request failed")
        return Response(
            {"error": "La génération du batch a échoué."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    return Response(batch)
