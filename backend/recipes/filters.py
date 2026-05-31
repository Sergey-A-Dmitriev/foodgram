from django.contrib import admin

from recipes.constants import FAST_LIMIT, MEDIUM_LIMIT


class HasRelationFilter(admin.SimpleListFilter):
    """Базовый фильтр наличия связи."""

    related_name = ''

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'))

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

    TIME_RANGES = {
        'fast': (0, FAST_LIMIT - 1),
        'medium': (FAST_LIMIT, MEDIUM_LIMIT - 1),
        'slow': (MEDIUM_LIMIT, 10**9)}

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        counts = {
            key: qs.filter(cooking_time__range=value).count()
            for key, value in self.TIME_RANGES.items()}

        return (
            ('fast', f'Быстро (<10 мин) ({counts["fast"]})'),
            ('medium', f'Средне (10–30 мин) ({counts["medium"]})'),
            ('slow', f'Долго (>30 мин) ({counts["slow"]})'))

    def queryset(self, request, recipes):
        value = self.value()
        if value in self.TIME_RANGES:
            return recipes.filter(
                cooking_time__range=self.TIME_RANGES[value])
        return recipes
