from django.contrib import admin


class HasRelationFilter(admin.SimpleListFilter):
    """Базовый фильтр наличия связи."""

    LOOKUPS = (('yes', 'Да'),
               ('no', 'Нет'))

    related_name = ''

    def lookups(self, request, model_admin):
        return self.LOOKUPS

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

    CACHE_KEY = 'cooking_time_quantiles'

    def get_buckets(self, queryset):
        values = list(queryset.values_list('cooking_time', flat=True))
        if len(values) < 3:
            return None
        values = sorted(values)
        fast_threshold = values[len(values) // 3]
        slow_threshold = values[(2 * len(values)) // 3]
        return fast_threshold, slow_threshold

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        quantiles = self.get_buckets(recipes)
        if not quantiles:
            return (
                ('fast', 'Быстро (0)'),
                ('medium', 'Средне (0)'),
                ('slow', 'Долго (0)'))
        fast_threshold, slow_threshold = quantiles
        fast_count = recipes.filter(cooking_time__lte=fast_threshold).count()
        medium_count = (recipes.filter(cooking_time__gt=fast_threshold,
                                       cooking_time__lte=slow_threshold)
                        .count())
        slow_count = recipes.filter(cooking_time__gt=slow_threshold).count()

        return (
            ('fast', f'Быстро ({fast_count})'),
            ('medium', f'Средне ({medium_count})'),
            ('slow', f'Долго ({slow_count})'))

    def queryset(self, request, queryset):
        quantiles = self.get_buckets(queryset)
        if not quantiles:
            return queryset
        fast_threshold, slow_threshold = quantiles
        value = self.value()
        if value == 'fast':
            return queryset.filter(cooking_time__lte=fast_threshold)
        if value == 'medium':
            return queryset.filter(cooking_time__gt=fast_threshold,
                                   cooking_time__lte=slow_threshold)
        if value == 'slow':
            return queryset.filter(cooking_time__gt=slow_threshold)
        return queryset


class UsedInRecipesFilter(HasRelationFilter):
    title = 'Используется в рецептах'
    parameter_name = 'used_in_recipes'
    related_name = 'recipe_ingredients'
