from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.Serializer):
    class Meta:
        model = Recipe
        fields = ["id", "title", "description", "price", "time_minutes"]
        read_only_fields = ["id"]
