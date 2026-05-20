import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

DATA_PATH = ''


class Command(BaseCommand):
    """Загрузчик для CSV."""

    help = 'Загрузка данных из CSV'

    def handle(self, *args, **kwargs):
        """Метод handle."""
        self.load_ingredients()
        self.stdout.write(self.style.SUCCESS('Данные загружены!'))

    def load_ingredients(self):
        """Метод загрузчик."""
        with open(f'{DATA_PATH}ingredients.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'],)
