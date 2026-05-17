from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import Recipe
from users.models import Subscription

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        """Служебный класс."""

        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')

    def create(self, validated_data):
        """Метод для создания пользователя."""
        password = validated_data.pop('password')
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''))
        user.set_password(password)
        user.save()
        return user


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого рецепта."""

    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Служебный класс."""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    """Основной сериализатор пользователя."""

    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Служебный класс."""

        model = User

        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed', 'avatar')

    @extend_schema_field(serializers.BooleanField)
    def get_is_subscribed(self, obj):
        """Проверка на наличие подписки."""
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return False
        if request.user == obj:
            return False

        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""

    avatar = Base64ImageField()

    class Meta:
        """Служебный класс."""

        model = User
        fields = ('avatar',)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta:
        """Служебный класс."""

        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Получить N последних рецептов пользователя."""
        recipes = obj.recipes.all()
        request = self.context.get('request')

        recipes_limit = request.GET.get('recipes_limit')

        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        return ShortRecipeSerializer(
            recipes,
            many=True
        ).data

    def get_recipes_count(self, obj):
        """Получить количество рецептов пользователя."""
        return obj.recipes.count()


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для установки нового пароля."""

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_current_password(self, value):
        """Валидатор текущего пароля."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Текущий пароль введен неверно')
        return value

    def validate_new_password(self, value):
        """Валидатор нового пароля."""
        validate_password(value)
        return value
