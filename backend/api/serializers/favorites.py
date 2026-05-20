from api.mixins import RepresentationMixin
from recipes.models import Favorite, ShoppingCart
from rest_framework import serializers


class FavoriteSerializer(RepresentationMixin, serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        """Служебный класс."""

        model = Favorite
        fields = ('id', 'user', 'recipe', 'created_at')
        read_only_fields = ('created_at',)

    def validate(self, data):
        """Проверка: не добавлен ли уже рецепт в избранное."""
        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError('Рецепт уже в избранном')
        return data


class ShoppingCartSerializer(RepresentationMixin, serializers.ModelSerializer):
    """Сериализатор для покупок."""

    class Meta:
        """Служебный класс."""

        model = ShoppingCart
        fields = ('id', 'user', 'recipe', 'added_at')
        read_only_fields = ('added_at',)

    def validate(self, data):
        """Проверка на наличие рецепта в корзине."""
        if ShoppingCart.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже в корзине')
        return data
