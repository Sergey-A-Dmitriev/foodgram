from django.contrib import admin


class RecipesCountMixin:
    """Миксин для подсчёта рецептов."""

    recipes_field = 'recipes'
    list_display = ('get_recipes_count',)

    @admin.display(description='Рецептов')
    def get_recipes_count(self, recipes):
        return recipes.recipes.count()
