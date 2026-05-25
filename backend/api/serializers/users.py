from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from recipes.models import Recipe, Subscription

User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta(DjoserUserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого рецепта."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Служебный класс."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(DjoserUserSerializer):
    """Основной сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',)

        read_only_fields = fields

    @extend_schema_field(serializers.BooleanField)
    def get_is_subscribed(self, account):
        """Проверка на наличие подписки."""

        request = self.context.get('request')

        return bool(
            request
            and request.user.is_authenticated
            and request.user != account
            and Subscription.objects.filter(
                user=request.user,
                author=account).exists())


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField()

    class Meta:
        """Служебный класс."""

        model = User
        fields = ('avatar',)


class SubscriptionAuthorSerializer(UserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:

        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'avatar',
                  'recipes',
                  'recipes_count',)

        read_only_fields = fields

    def get_recipes(self, recipes):
        """Получить N последних рецептов пользователя."""
        recipes = recipes.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes,
            many=True).data
