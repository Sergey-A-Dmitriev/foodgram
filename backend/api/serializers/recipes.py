from drf_extra_fields.fields import Base64ImageField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from api.serializers.users import UserSerializer
from recipes.constants import MIN_AMOUNT_VALUE, MIN_TIME_COOK_VALUE
from recipes.models import (Ingredient, Recipe,
                            RecipeIngredient, Tag)


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
        read_only_fields = fields


class RecipeIngredientWriteSerializer(serializers.Serializer):
    """Сериализатор для записи игредиентов в рецепт (POST/PATCH)."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT_VALUE)


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
    image = serializers.ImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Служебный класс."""

        model = Recipe
        fields = ('id', 'tags', 'name', 'text', 'ingredients', 'author',
                  'image', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')
        read_only_fields = fields

    def _is_relation_exists(self, recipe, model_name):
        """Проверка существования связи user ↔ recipe."""

        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        user_id = request.user.id
        return any(
            rel.user_id == user_id
            for rel in getattr(recipe, model_name).all())

    @extend_schema_field(serializers.BooleanField)
    def get_is_favorited(self, recipe):
        return self._is_relation_exists(recipe, 'favorites')


    @extend_schema_field(serializers.BooleanField)
    def get_is_in_shopping_cart(self, recipe):
        return self._is_relation_exists(recipe, 'shopping_carts')


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
    cooking_time = serializers.IntegerField(
        min_value=MIN_TIME_COOK_VALUE)

    class Meta:
        """Служебный класс."""

        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def create_ingredients(self, ingredients, recipe):
        """Метод для создания ингредиентов в рецепте."""
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],   # ← уже объект Ingredient
                amount=item['amount'])
            for item in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        """Метод для создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create({
            **validated_data,
            'author': self.context['request'].user})
        recipe.author = self.context['request'].user
        recipe.save()
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        """Метод для обновления рецепта."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        recipe = super().update(recipe, validated_data)
        if tags is not None:
            recipe.tags.set(tags)
        if ingredients is not None:
            recipe.recipe_ingredients.all().delete()
            self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        """Метод для представления рецепта."""
        return RecipeReadSerializer(
            instance,
            context=self.context).data

    def _validate_duplicates(self, records_id, field_name):
        duplicates = {
            record_id for record_id in records_id
            if records_id.count(record_id) > 1}
        if duplicates:
            raise serializers.ValidationError(
                f'Повторяются {field_name}: {duplicates}')

    def validate(self, data):
        """Общая валидация."""

        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Должен быть хотя бы один ингредиент')
        ingredient_ids = [
            ingredient['id']
            for ingredient in ingredients]
        self._validate_duplicates(ingredient_ids, 'ингредиенты')

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Должен быть хотя бы один тег')
        tag_ids = [tag.id for tag in tags]
        self._validate_duplicates(tag_ids, 'теги')
        return data
