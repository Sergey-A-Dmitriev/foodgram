from django.contrib import admin


class RecipesCountMixin:
    """Миксин для подсчёта рецептов."""

    @admin.display(description='Количество рецептов')
    def get_recipes_count(self, recipes):
        return recipes.recipes.count()
