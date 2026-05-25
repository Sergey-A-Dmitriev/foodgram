from recipes.management.commands.load_json_base import BaseLoadJSONCommand
from recipes.models import Ingredient


class Command(BaseLoadJSONCommand):
    """Загрузка ингредиентов."""

    model = Ingredient
    file_name = 'ingredients.json'
    fields = ('name', 'measurement_unit')
