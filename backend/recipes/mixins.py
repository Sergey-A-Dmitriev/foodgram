from django.contrib import admin


class RecipesCountMixin:
    """Миксин для подсчёта рецептов."""

    list_display = ('get_recipes_count',)

    @admin.display(description='Рецептов')
    def get_recipes_count(self, obj):
        return self._get_recipes_queryset(obj).count()

    def _get_recipes_queryset(self, obj):
        raise NotImplementedError
