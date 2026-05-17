from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.fields import Base64ImageField
from api.serializers.users import UserSerializer
from recipes.constants import MAX_AMOUNT_VALUE, MIN_AMOUNT_VALUE
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        """Служебный класс."""

        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Служебный класс."""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения игредиентов в рецепте (GET)."""

    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        """Служебный класс."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """Сериализатор для записи игредиентов в рецепт (POST/PATCH)."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT_VALUE,
        max_value=MAX_AMOUNT_VALUE)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта (GET)."""

    tags = TagSerializer(
        many=True,
        read_only=True)
    author = UserSerializer(
        read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredients')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Служебный класс."""

        model = Recipe
        fields = ('id', 'tags', 'name', 'text', 'ingredients', 'author',
                  'image', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    @extend_schema_field(serializers.BooleanField)
    def get_is_favorited(self, obj):
        """Метод для проверки наличия рецепта в избранном."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj).exists()

    @extend_schema_field(serializers.BooleanField)
    def get_is_in_shopping_cart(self, obj):
        """Метод для проверки наличия рецепта в покупках."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления рецептов."""

    image = Base64ImageField(required=True,
                             allow_null=False,
                             allow_empty_file=False)
    ingredients = RecipeIngredientWriteSerializer(
        many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)

    class Meta:
        """Служебный класс."""

        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def create_ingredients(self, ingredients, recipe):
        """Метод для создания ингредиентов в рецепте."""
        recipe_ingredients = []

        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(
                id=ingredient_data['id'])
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']))
        RecipeIngredient.objects.bulk_create(
            recipe_ingredients)

    def create(self, validated_data):
        """Метод для создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Метод для обновления рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Метод для представления рецепта."""
        return RecipeReadSerializer(
            instance,
            context=self.context).data

    def validate_image(self, value):
        """Проверка наличия фото рецепта."""
        if not value:
            raise serializers.ValidationError(
                'Изображение обязательно')
        return value

    def validate_cooking_time(self, value):
        """Проверка времени приготовления."""
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0')
        if value > 1440:
            raise serializers.ValidationError(
                'Время приготовления не может превышать 1440 минут (24 часа)')
        return value

    def validate(self, data):
        """Общая валидация."""
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Должен быть хотя бы один ингредиент')

        ingredient_ids = []
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    f"Должно быть больше 0, получено: {ingredient['amount']}")

            if ingredient['id'] in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться')

            ingredient_ids.append(ingredient['id'])

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Должен быть тег')

        tag_ids = []
        for tag in tags:
            if tag.id in tag_ids:
                raise serializers.ValidationError(
                    'Теги не должны повторяться')
            tag_ids.append(tag.id)
        return data
