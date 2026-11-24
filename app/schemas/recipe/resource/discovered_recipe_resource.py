"""Recipe suggestion exposed to the frontend."""

from pydantic import BaseModel

from ..data import RecipeData


class DiscoveredIngredientResource(BaseModel):
    name: str
    quantity: float
    unit: str | None


class DiscoveredRecipeStepResource(BaseModel):
    instruction: str


class DiscoveredRecipeResource(BaseModel):
    name: str
    description: str | None
    preparationTime: int
    cookingTime: int
    ingredients: list[DiscoveredIngredientResource]
    steps: list[DiscoveredRecipeStepResource]
    mealTimes: list[str]
    imageDataUrl: str | None
    imageGenerationFailed: bool

    @classmethod
    def from_data(
        cls,
        data: RecipeData,
        *,
        image_data_url: str | None,
        image_generation_failed: bool,
    ) -> "DiscoveredRecipeResource":
        return cls(
            name=data.name,
            description=data.description,
            preparationTime=data.preparation_time,
            cookingTime=data.cooking_time,
            ingredients=[
                DiscoveredIngredientResource(
                    name=ingredient.name,
                    quantity=float(ingredient.quantity),
                    unit=ingredient.unit,
                )
                for ingredient in data.ingredients
            ],
            steps=[
                DiscoveredRecipeStepResource(instruction=step.instruction)
                for step in data.steps
            ],
            mealTimes=data.meal_times,
            imageDataUrl=image_data_url,
            imageGenerationFailed=image_generation_failed,
        )
