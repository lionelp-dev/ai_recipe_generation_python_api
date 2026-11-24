"""Validation schema for recipe-discovery criteria."""

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator


class DiscoverRecipesRequest(BaseModel):
    """Validated criteria used to discover recipes."""

    model_config = ConfigDict(str_strip_whitespace=True)

    prompt: StrictStr = Field(min_length=3, max_length=5000)
    selected_meal_times: list[StrictStr] = Field(
        default_factory=list,
        alias="selectedMealTimes",
        max_length=4,
    )

    @field_validator("selected_meal_times")
    @classmethod
    def validate_meal_times(cls, meal_times: list[str]) -> list[str]:
        if any(not meal_time for meal_time in meal_times):
            raise ValueError("Les moments de repas sont invalides.")
        return list(dict.fromkeys(meal_times))
