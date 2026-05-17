from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Регистрация модели Tag."""

    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Регистрация модели Ингредиент."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    """Вставка IngredientAmount."""

    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Регистрация модели Рецепт."""

    list_display = ('id', 'name', 'author', 'favorites_count')
    list_filter = ('tags', 'author')
    search_fields = ('name', 'author__username')
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
    def favorites_count(self, obj):
        """Подсчет количества в избранном."""
        return obj.favorites.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Регистрация сводной модели RecipeIngredient."""

    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__title', 'ingredient__name')
    autocomplete_fields = ['recipe', 'ingredient']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Регистрация модели Избранное."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Регистрация модели Покупки."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__title')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Регистрация модели Подписки."""

    list_display = ('user', 'author')
    search_fields = ('follower__username', 'following__username')
