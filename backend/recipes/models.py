from django.db import models
from django.core.validators import RegexValidator
from users.models import User

class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, validators=[
        RegexValidator(r'^[-a-zA-Z0-9_]+$')])
    color = models.CharField(max_length=7, validators=[
        RegexValidator(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')])

class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    image = models.ImageField(upload_to='recipes/')
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(
        'Ingredient', 
        through='RecipeIngredient'
    )

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')