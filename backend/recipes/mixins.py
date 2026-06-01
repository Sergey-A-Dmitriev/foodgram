from django.contrib import admin


class RecipesCountMixin:
    """Миксин для подсчёта рецептов."""

    list_display = ('get_recipes_count',)
    related_name = ''

    @admin.display(description='Рецептов')
    def get_recipes_count(self, recipes):
        return getattr(recipes, self.related_name).count()
