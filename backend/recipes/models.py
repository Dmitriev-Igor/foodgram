from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

LENGTH_TEXT = 20
User = get_user_model()


class Tag(models.Model):
    """Модель тегов для рецептов."""

    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[RegexValidator(r'^[-a-zA-Z0-9_]+$')],
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:LENGTH_TEXT]


class Ingredient(models.Model):
    """Модель ингредиентов для рецептов."""

    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = [('name', 'measurement_unit')]
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'[:LENGTH_TEXT]


class Recipe(models.Model):
    """Модель рецептов."""

    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        'Название',
        max_length=256,
        db_index=True,
    )
    image = models.ImageField(
        'Ссылка на картинку на сайте',
        upload_to='recipes/',
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=(
            MinValueValidator(
                1,
                message='Время не может быть меньше 1 минуты!',
            ),
        ),
    )
    created_at = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name[:LENGTH_TEXT]


class RecipeIngredient(models.Model):
    """Модель связи ингредиентов с рецептами с указанием количества."""

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
        'Количество ингридиента',
        validators=(
            MinValueValidator(
                1,
                message='Количество ингредиента не может быть меньше 1!'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Связь ингредиента и рецепта'
        verbose_name_plural = 'Связи ингредиентов и рецептов'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.recipe} содержит ингредиент/ты {self.ingredient}'


class UserRecipe(models.Model):
    """Абстрактная модель для избранного и списка покупок."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta:
        abstract = True
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_%(class)s',
            ),
        )


class Favorite(UserRecipe):
    """Модель для избранных рецептов пользователя."""

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(UserRecipe.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(UserRecipe):
    """Модель для списка покупок пользователя."""

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        default_related_name = 'shopping_carts'

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
