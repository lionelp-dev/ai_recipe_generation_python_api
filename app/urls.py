from django.urls import path

from .views.api import discover_recipes_api

urlpatterns = [
    path(
        "internal/recipes/discover/",
        discover_recipes_api,
        name="internal_discover_recipes",
    ),
    path("internal/recipes/discover", discover_recipes_api),
]
