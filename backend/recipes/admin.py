from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель для модели Tag."""

    list_display = ('name', 'slug', 'recipe_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True
    list_per_page = 20

    @admin.display(description='Рецептов с тегом')
    def recipe_count(self, obj):
        """Возвращает количество рецептов с тегом."""
        return obj.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель для модели Ingredient."""

    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    ordering = ('name',)

    @admin.display(description='Используется в рецептах')
    def recipe_count(self, obj):
        """Возвращает количество рецептов с ингредиентом."""
        return obj.recipeingredients.count()

    def save_model(self, request, obj, form, change):
        """Проверяет уникальность ингредиента перед сохранением."""
        if Ingredient.objects.filter(
            name__iexact=obj.name,
            measurement_unit__iexact=obj.measurement_unit
        ).exclude(pk=obj.pk).exists():
            raise ValidationError('Такой ингредиент уже существует!')
        super().save_model(request, obj, form, change)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель для модели Recipe."""

    list_display = ('name', 'author', 'favorite_count',
                    'cooking_time', 'created_at', 'image_preview')
    search_fields = ('name', 'author__username', 'text')
    list_filter = ('tags', 'author', 'created_at')
    filter_horizontal = ('tags', 'ingredients')
    autocomplete_fields = ['author']
    readonly_fields = ('created_at', 'image_preview')
    date_hierarchy = 'created_at'
    save_on_top = True
    list_per_page = 25

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        """Возвращает количество добавлений рецепта в избранное."""
        return obj.favorites.count()

    @admin.display(description='Превью')
    def image_preview(self, obj):
        """Отображает миниатюру изображения рецепта."""
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "Нет изображения"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админ-панель для модели RecipeIngredient."""

    list_display = ('recipe', 'ingredient', 'amount')
    autocomplete_fields = ['recipe', 'ingredient']
    search_fields = ('recipe__name', 'ingredient__name')
    list_per_page = 50


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-панель для модели ShoppingCart."""

    list_display = ('user', 'recipe', 'created_at')
    autocomplete_fields = ['user', 'recipe']
    date_hierarchy = 'created_at'
    list_per_page = 50


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-панель для модели Favorite."""

    list_display = ('user', 'recipe', 'created_at')
    autocomplete_fields = ['user', 'recipe']
    date_hierarchy = 'created_at'
    list_per_page = 50
