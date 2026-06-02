from django.contrib import admin

from recipes.models import Tag


class TagFilter(admin.SimpleListFilter):
    title = 'Тег'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        return Tag.objects.values_list('pk', 'name')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags=self.value())
        return queryset


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

    def _get_time_ranges(self, recipes_qs):
        cooking_times = tuple(
            recipes_qs.order_by('cooking_time')
            .values_list('cooking_time', flat=True)
            .distinct())
        fast_threshold = (
            cooking_times[len(cooking_times) // 3])
        slow_threshold = (
            cooking_times[(2 * len(cooking_times)) // 3])

        return {
            'fast': (
                cooking_times[0],
                fast_threshold,),
            'medium': (
                fast_threshold + 1,
                slow_threshold,),
            'slow': (
                slow_threshold + 1,
                cooking_times[-1],)}

    def lookups(self, request, model_admin):
        time_ranges = self._get_time_ranges(
            model_admin.model.objects.all())

        if not time_ranges:
            return ()

        return (
            ('fast',
                f'Быстрые (до {time_ranges["fast"][1]} мин)'),
            ('medium',
                f'Средние ({time_ranges["medium"][0]}–'
                f'{time_ranges["medium"][1]} мин)'),
            ('slow',
                f'Долгие (от {time_ranges["slow"][0]} мин)'))

    def queryset(self, request, recipes_qs):
        time_ranges = self._get_time_ranges(recipes_qs)

        if not time_ranges:
            return recipes_qs

        selected_range = time_ranges.get(self.value())

        if selected_range:
            return recipes_qs.filter(
                cooking_time__range=selected_range)

        return recipes_qs


class UsedInRecipesFilter(HasRelationFilter):
    title = 'Используется в рецептах'
    parameter_name = 'used_in_recipes'
    related_name = 'recipe_ingredients'
