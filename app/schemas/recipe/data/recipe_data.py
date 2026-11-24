"""Validated recipe data used inside the application."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError


class RecipeIngredientData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    unit: str | None = Field(default=None, max_length=50)

    @field_validator("unit", mode="before")
    @classmethod
    def empty_unit_is_none(cls, value: Any) -> str | None:
        return value.strip() or None if isinstance(value, str) else None


class RecipeStepData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    instruction: str = Field(min_length=1, max_length=2000)


class RecipeData(BaseModel):
    """Validated recipe payload used by both manual and generated recipes."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    preparation_time: int = Field(ge=0)
    cooking_time: int = Field(ge=0)
    ingredients: list[RecipeIngredientData] = Field(default_factory=list)
    steps: list[RecipeStepData] = Field(default_factory=list)
    meal_times: list[str] = Field(default_factory=list)

    @field_validator("description", mode="before")
    @classmethod
    def empty_description_is_none(cls, value: Any) -> str | None:
        return value.strip() or None if isinstance(value, str) else None

    @field_validator("meal_times")
    @classmethod
    def meal_times_must_be_known(
        cls, value: list[str], info: ValidationInfo
    ) -> list[str]:
        context = info.context or {}
        known_meal_times = set(context.get("known_meal_times", []))
        if "known_meal_times" in context and any(slug not in known_meal_times for slug in value):
            raise PydanticCustomError(
                "unknown_meal_time", "Un moment de repas sélectionné est invalide."
            )
        return value

    @model_validator(mode="after")
    def generated_recipes_need_a_step(self, info: ValidationInfo) -> Self:
        if info.context and info.context.get("generated"):
            if not self.steps:
                raise PydanticCustomError(
                    "generated_steps_required", "Une suggestion doit comporter au moins une étape."
                )
            if not self.meal_times:
                raise PydanticCustomError(
                    "generated_meal_times_required",
                    "Une suggestion doit comporter un moment de repas.",
                )
        return self
