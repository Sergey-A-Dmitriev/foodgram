from api.serializers.users import ShortRecipeSerializer


class RepresentationMixin:
    """Миксин to_representation."""

    def to_representation(self, instance):
        """Возвращает краткую информацию о рецепте."""
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
