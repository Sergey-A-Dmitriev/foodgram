from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Recipe


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого рецепта."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
