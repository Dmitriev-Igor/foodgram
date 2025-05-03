import csv
import os

from config.settings import CSV_FILES_DIR
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        csv_file = 'ingredients.csv'
        csv_path = os.path.join(CSV_FILES_DIR, csv_file)
        try:
            with open(csv_path, encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                ingredients = [
                    Ingredient(name=item[0], measurement_unit=item[1])
                    for item in reader
                ]
                Ingredient.objects.bulk_create(ingredients)
        except FileNotFoundError:
            print(f'Файл {csv_file} не найден!')
