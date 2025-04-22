"""Модуль для работы с корзиной покупок."""

from datetime import date
from django.db.models import Sum
from django.http import HttpResponse
from recipes.models import RecipeIngredient


def get_shopping_cart_textfile(user):
    """
    Формирует текстовый файл списка покупок.
    
    Args:
        user: Пользователь, для которого формируется список покупок.
    
    Returns:
        HttpResponse: Ответ с текстовым файлом списка покупок.
    """
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_carts__user=user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit',
    ).annotate(
        total_amount=Sum('amount', distinct=True)
    ).order_by('ingredient__name')

    current_date = date.today().strftime('%d.%m.%Y')
    lines = [f'Список покупок на {current_date}:\n']

    for item in ingredients:
        name = item['ingredient__name']
        amount = item['total_amount']
        unit = item['ingredient__measurement_unit']
        lines.append(f'{name} - {amount} {unit}')

    response = HttpResponse(
        content='\n'.join(lines),
        content_type='text/plain'
    )
    response['Content-Disposition'] = 'attachment; filename=ShoppingList.txt'

    return response