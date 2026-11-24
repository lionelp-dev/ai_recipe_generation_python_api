"""Schema for a recipe submitted to the application."""

from decimal import Decimal
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from ..data import RecipeData


class RecipeIngredientRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    quantity: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    unit: str | None = Field(default=None, max_length=50)

    @field_validator("unit", mode="before")
    @classmethod
    def empty_unit_is_none(cls, value: Any) -> str | None:
        return value.strip() or None if isinstance(value, str) else None


class RecipeStepRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    instruction: str = Field(min_length=1, max_length=2000)


class RecipeRequest(BaseModel):
    """Validated external recipe payload, convertible to internal recipe data."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    preparation_time: int = Field(
        ge=0,
        validation_alias=AliasChoices("preparationTime", "preparation_time"),
    )
    cooking_time: int = Field(
        ge=0,
        validation_alias=AliasChoices("cookingTime", "cooking_time"),
    )
    ingredients: list[RecipeIngredientRequest] = Field(default_factory=list)
    steps: list[RecipeStepRequest] = Field(default_factory=list)
    meal_times: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("mealTimes", "meal_times"),
    )

    @field_validator("description", mode="before")
    @classmethod
    def empty_description_is_none(cls, value: Any) -> str | None:
        return value.strip() or None if isinstance(value, str) else None

    def to_data(
        self,
        *,
        known_meal_times: list[str] | None = None,
        generated: bool = False,
    ) -> RecipeData:
        context: dict[str, object] = {"generated": generated}
        if known_meal_times is not None:
            context["known_meal_times"] = known_meal_times
        return RecipeData.model_validate(self.model_dump(), context=context)
