from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (INGREDIENT_NAME_MAX_LENGTH, MAX_AMOUNT,
                        MAX_COOKING_TIME, MEASUREMENT_UNIT_MAX_LENGTH,
                        MIN_AMOUNT, MIN_COOKING_TIME, RECIPE_NAME_MAX_LENGTH,
                        TAG_NAME_MAX_LENGTH, TAG_SLUG_MAX_LENGTH,
                        TEXT_TRUNCATION)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:TEXT_TRUNCATION]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = [('name', 'measurement_unit')]
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'[:TEXT_TRUNCATION]


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        null=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=RECIPE_NAME_MAX_LENGTH,
        db_index=True
    )
    image = models.ImageField(
        verbose_name='Ссылка на картинку на сайте',
        upload_to='recipes/'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Время не может быть меньше {MIN_COOKING_TIME} минуты'
            ),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )
    created_at = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name[:TEXT_TRUNCATION]


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        related_name='recipeingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message=f'Количество не может быть меньше {MIN_AMOUNT}!'
            ),
            MaxValueValidator(MAX_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = 'Связь ингредиента и рецепта'
        verbose_name_plural = 'Связи ингредиентов и рецептов'
        ordering = ('ingredient__name',)
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.recipe} содержит {self.ingredient}'[:TEXT_TRUNCATION]


class UserRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ('-recipe__created_at',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_%(class)s'
            ),
        )


class Favorite(UserRecipe):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(UserRecipe.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'[:TEXT_TRUNCATION]


class ShoppingCart(UserRecipe):
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta(UserRecipe.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_carts'

    def __str__(self):
        return f'{self.recipe} в списке покупок {self.user}'[:TEXT_TRUNCATION]
