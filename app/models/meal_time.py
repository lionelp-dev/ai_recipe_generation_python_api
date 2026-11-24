from __future__ import annotations

from django.db import models


class MealTime(models.TextChoices):
    BREAKFAST = "breakfast", "Petit-déjeuner"
    LUNCH = "lunch", "Déjeuner"
    DINNER = "diner", "Dîner"
    SNACK = "snack", "Collation"


def meal_time_options() -> list[dict[str, str]]:
    return [{"slug": value, "label": label} for value, label in MealTime.choices]


def selected_meal_time_options(slugs: list[str]) -> list[dict[str, str]]:
    return [
        {"slug": slug, "label": MealTime(slug).label}
        for slug in slugs
        if slug in MealTime.values
    ]
