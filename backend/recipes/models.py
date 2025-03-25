from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    image = models.ImageField(upload_to='recipes/')
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField(
        'ingredients.Ingredient',
        through='RecipeIngredient'
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        'ingredients.Ingredient', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=32,
        unique=True
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=32,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Слаг содержит недопустимые символы'
            )
        ]
    )
    color = models.CharField(  # Добавим цвет для фронтенда
        'Цветовой HEX-код',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Некорректный HEX-код цвета'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
