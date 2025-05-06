import json
import os

from config.settings import JSON_FILES_DIR
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        json_file = 'ingredients.json'
        json_path = os.path.join(JSON_FILES_DIR, json_file)
        try:
            with open(json_path, encoding='utf-8') as file:
                data = json.load(file)
                ingredients = [
                    Ingredient(
                        name=item['name'],
                        measurement_unit=item['measurement_unit'])
                    for item in data
                ]
                Ingredient.objects.bulk_create(ingredients)
        except FileNotFoundError:
            print(f'Файл {json_file} не найден!')
        except json.JSONDecodeError:
            print(f'Ошибка при декодировании JSON в файле {json_file}!')
