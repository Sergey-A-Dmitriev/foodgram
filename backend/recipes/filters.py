import django_filters
from django.contrib import admin
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    """Фильтр для поиска ингридентов по имени."""

    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов по автору."""

    available_tags = Tag.objects.all()
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=available_tags)

    author = django_filters.NumberFilter(
        field_name='author__id')

    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')

    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:

        model = Recipe
        fields = ['tags', 'author', 'is_in_shopping_cart', 'is_favorited']

    def filter_is_in_shopping_cart(self, recipes, name, is_in_cart):
        """Для фильтрации рецептов по пользователю в покупках."""
        user = self.request.user
        if not user.is_authenticated:
            return recipes.none()
        if is_in_cart:
            return recipes.filter(
                shopping_carts__user=user
            ).distinct()
        return recipes

    def filter_is_favorited(self, recipes, name, is_in_favorited):
        """Для фильтрации рецептов по пользователю в избранном."""
        user = self.request.user
        if not user.is_authenticated:
            return recipes.none()
        if is_in_favorited:
            return recipes.filter(
                favorites__user=user
            ).distinct()
        return recipes


class YesNoFilter(admin.SimpleListFilter):
    """Базовый yes/no фильтр."""

    def lookups(self, request, model_admin):
        return (('yes', 'Да'),
                ('no', 'Нет'),)


class HasRelationFilter(YesNoFilter):
    """Базовый фильтр наличия связи."""

    related_name: str = ''

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(
                **{f'{self.related_name}__isnull': False}
            ).distinct()
        if value == 'no':
            return queryset.filter(
                **{f'{self.related_name}__isnull': True})
        return queryset


class HasRecipesFilter(HasRelationFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'
    related_name = 'recipes'


class HasSubscriptionsFilter(HasRelationFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    related_name = 'subscriptions'


class HasFollowersFilter(HasRelationFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_followers'
    related_name = 'author_subscriptions'


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_group'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)

        fast = qs.filter(cooking_time__lt=10).count()
        medium = qs.filter(cooking_time__gte=10, cooking_time__lt=30).count()
        slow = qs.filter(cooking_time__gte=30).count()

        return (('fast', f'Быстро (<10 мин) ({fast})'),
                ('medium', f'Средне (10–30 мин) ({medium})'),
                ('slow', f'Долго (≥30 мин) ({slow})'),)

    def queryset(self, request, recipes):
        value = self.value()
        if value == 'fast':
            return recipes.filter(cooking_time__lt=10)
        if value == 'medium':
            return recipes.filter(
                cooking_time__gte=10,
                cooking_time__lt=30)
        if value == 'slow':
            return recipes.filter(cooking_time__gte=30)
        return recipes
