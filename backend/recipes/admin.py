from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from api.filters import (CookingTimeFilter, HasFollowersFilter,
                         HasRecipesFilter, HasSubscriptionsFilter)
from api.mixins import RecipesCountMixin
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag, User)


class UserRecipeAdmin(admin.ModelAdmin):
    """Базовый класс для моделей user-recipe."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(User)
class UserAdmin(RecipesCountMixin, UserAdmin):
    """Регистрация кастомной модели User."""

    list_display = ('id', 'username', 'get_full_name', 'email', 'get_avatar',
                    'get_recipes_count', 'get_subscriptions_count',
                    'get_followers_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active',
                   HasRecipesFilter, HasSubscriptionsFilter,
                   HasFollowersFilter)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('avatar',)}),)

    @admin.display(description='ФИО')
    def get_full_name(self, account):
        return f'{account.first_name} {account.last_name}'

    @admin.display(description='Аватар')
    def get_avatar(self, account):
        if account.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%;" />',
                account.avatar.url)
        return '—'

    @admin.display(description='Подписки')
    def get_subscriptions_count(self, account):
        return account.subscriptions.count()

    @admin.display(description='Подписчики')
    def get_followers_count(self, account):
        return account.subscriptions_as_author.count()

@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Регистрация модели Tag."""

    list_display = ('id', 'name', 'slug', 'get_recipes_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Регистрация модели Ингредиент."""

    list_display = ('id', 'name', 'measurement_unit', 'get_recipes_count')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)

    @admin.display(description='Количество рецептов')
    def get_recipes_count(self, ingredient):
        return (Recipe.objects.filter(
            recipe_ingredients__ingredient=ingredient).count())


class RecipeIngredientInline(admin.TabularInline):
    """Вставка IngredientAmount."""

    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Регистрация модели Рецепт."""

    list_display = ('id', 'name', 'cooking_time', 'author',
                    'get_favorites_count', 'get_ingredients',
                    'get_tags', 'get_image')
    list_filter = ('tags', 'author', CookingTimeFilter)
    search_fields = ('name', 'author__username', 'tags__name',
                     'tags__slug', 'recipe_ingredients__ingredient__name',)
    inlines = [RecipeIngredientInline]
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'author', 'text', 'image')}),
        ('Детали', {
            'fields': ('cooking_time', 'tags')}),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)}),
    )

    @admin.display(description='В избранном')
    def get_favorites_count(self, recipes):
        """Подсчет количества в избранном."""
        return recipes.favorites.count()

    @admin.display(description='Продукты')
    def get_ingredients(self, recipe):
        return mark_safe(
            '<br>'.join(
                f'{ri.ingredient.name} — {ri.amount} '
                f'{ri.ingredient.measurement_unit}'
                for ri in recipe.recipe_ingredients.all())
        )

    @admin.display(description='Изображение')
    def get_image(self, recipe):
        if recipe.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="border-radius:8px;" />',
                recipe.image.url)
        return '—'

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return format_html(
            '{}',
            ', '.join(tag.name for tag in recipe.tags.all()))

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Регистрация сводной модели RecipeIngredient."""

    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__title', 'ingredient__name')
    autocomplete_fields = ['recipe', 'ingredient']


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeAdmin):
    """Регистрация модели Избранное."""


@admin.register(ShoppingCart)
class ShoppingCartAdmin(UserRecipeAdmin):
    """Регистрация модели Покупки."""


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Регистрация модели Подписки."""

    list_display = ('user', 'author')
    search_fields = ('follower__username', 'following__username')
