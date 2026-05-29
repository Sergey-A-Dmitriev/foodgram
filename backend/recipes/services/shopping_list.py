from collections import defaultdict
from datetime import datetime


def generate_shopping_list(user, ingredients_qs):
    """Формирование списка покупок."""
    date = datetime.now().strftime('%d.%m.%Y')
    ingredients = defaultdict(
        lambda: {'amount': 0})
    recipes = set()
    for item in ingredients_qs:
        name = item['ingredient__name'].capitalize()
        unit = item['ingredient__measurement_unit']
        ingredients[(name, unit)]['amount'] += item['amount']
        recipes.add(
            f"{item['recipe__name']} "
            f"({item['recipe__author__username']})")
    product_lines = [
        f"{i}. {name} — {data['amount']} {unit}"
        for i, ((name, unit), data) in enumerate(
            ingredients.items(),
            start=1)]

    return '\n'.join([
        f'Список покупок от {date}',
        '',
        'Продукты:',
        *product_lines,
        '',
        'Рецепты:',
        *sorted(recipes),
    ])
