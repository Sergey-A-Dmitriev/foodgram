from recipes.management.commands.load_json_base import BaseLoadJSONCommand
from recipes.models import Ingredient


class Command(BaseLoadJSONCommand):
    """Загрузка продуктов."""

    model = Ingredient
    file_name = 'ingredients.json'
