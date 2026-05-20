from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes.constants import (MAX_AMOUNT_VALUE, MAX_TIME_COOK_VALUE,
                               MIN_AMOUNT_VALUE, MIN_TIME_COOK_VALUE,
                               SIZE_INGREDIENT_NAME_FIELD,
                               SIZE_RECIPE_NAME_FIELD, SIZE_TAG_FIELDS,
                               SIZE_TEXT_FIELD, SIZE_UNIT_FIELD)
from users.models import User


class Tag(models.Model):
    """Модель Теги."""

    name = models.CharField(
        max_length=SIZE_TAG_FIELDS,
        unique=True,
        verbose_name='Уникальное название')
    slug = models.SlugField(
        max_length=SIZE_TAG_FIELDS,
        unique=True,
        verbose_name='Уникальный слаг')

    class Meta:
        """Служебный класс."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        """Магический метод __str__."""
        return self.name


class Ingredient(models.Model):
    """Модель Ингредиенты."""

    name = models.CharField(
        max_length=SIZE_INGREDIENT_NAME_FIELD,
        unique=True,
        verbose_name='Название ингредиента')
    measurement_unit = models.CharField(
        max_length=SIZE_UNIT_FIELD,
        verbose_name='Единица измерения')

    class Meta:
        """Служебный класс."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        """Магический метод __str__."""
        return f'{self.name} ({self.measurement_unit})'[:SIZE_TEXT_FIELD]


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')
    name = models.CharField(
        max_length=SIZE_RECIPE_NAME_FIELD,
        verbose_name='Название')
    text = models.TextField(
        verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        help_text='Время в минутах',
        validators=[MinValueValidator(MIN_TIME_COOK_VALUE),
                    MaxValueValidator(MAX_TIME_COOK_VALUE)],
        verbose_name='Время приготовления (мин)')
    image = models.ImageField(
        upload_to='images/',
        verbose_name='Ссылка на картинку на сайте')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания')
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name='Теги')

    class Meta:
        """Служебный класс."""

        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['author', '-created_at']),
                   models.Index(fields=['-created_at'])]

    def __str__(self):
        """Магический метод __str__."""
        return self.name[:SIZE_TEXT_FIELD]


class RecipeIngredient(models.Model):
    """Связующая таблица: рецепт + ингредиент + количество."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT_VALUE),
                    MaxValueValidator(MAX_AMOUNT_VALUE)],
        verbose_name='Количество')

    class Meta:
        """Служебный класс."""

        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient')]
        indexes = [models.Index(fields=['recipe', 'ingredient'])]

    def __str__(self):
        """Магический метод __str__."""
        return (f'{self.recipe.name}: '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit} '
                f'{self.ingredient.name}')[:SIZE_TEXT_FIELD]


class Favorite(models.Model):
    """Модель Избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        """Служебный класс."""

        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite')]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        indexes = [models.Index(fields=['user']),
                   models.Index(fields=['recipe'])]

    def __str__(self):
        """Магический метод __str__."""
        return f'{self.user.username} → {self.recipe.name}'[:SIZE_TEXT_FIELD]


class ShoppingCart(models.Model):
    """Модель Список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Рецепт')

    class Meta:
        """Служебный класс."""

        default_related_name = 'shopping_carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart')]
        verbose_name = 'Для покупок'
        verbose_name_plural = 'Для покупок'
        indexes = [models.Index(fields=['user'])]

    def __str__(self):
        """Магический метод __str__."""
        return f'{self.user.username} → {self.recipe.name}'[:SIZE_TEXT_FIELD]
