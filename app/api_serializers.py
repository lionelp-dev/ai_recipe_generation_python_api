"""DRF serializer for recipe discovery input."""

from rest_framework import serializers

from app.models import MealTime


class DiscoverRecipesSerializer(serializers.Serializer):
    prompt = serializers.CharField(min_length=3, max_length=5000, trim_whitespace=True)
    selectedMealTimes = serializers.ListField(
        child=serializers.ChoiceField(choices=MealTime.values),
        required=False,
        default=list,
        max_length=4,
    )

    def validate_selectedMealTimes(self, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))
