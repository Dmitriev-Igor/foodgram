from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Favorite
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'recipe_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True
    list_per_page = 20

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Рецептов с тегом'

    def save_model(self, request, obj, form, change):
        if not obj.color.startswith('#'):
            raise ValidationError(
                "Цвет должен быть в формате HEX (например, #FF0000)")
        super().save_model(request, obj, form, change)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    ordering = ('name',)
    save_on_top = True
    list_per_page = 50

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Используется в рецептах'

    def save_model(self, request, obj, form, change):
        if Ingredient.objects.filter(
            name__iexact=obj.name,
            measurement_unit__iexact=obj.measurement_unit
        ).exclude(pk=obj.pk).exists():
            raise ValidationError('Такой ингредиент уже существует!')
        super().save_model(request, obj, form, change)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
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

    def favorite_count(self, obj):
        return obj.in_favorites.count()
    favorite_count.short_description = 'В избранном'

    def image_preview(self, obj):
        return obj.image.url if obj.image else 'Нет изображения'
    image_preview.short_description = 'Превью'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    autocomplete_fields = ['recipe', 'ingredient']
    search_fields = ('recipe__name', 'ingredient__name')
    list_per_page = 50


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
    autocomplete_fields = ['user', 'recipe']
    date_hierarchy = 'added_at'
    list_per_page = 50


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_at')
    autocomplete_fields = ['user', 'recipe']
    date_hierarchy = 'created_at'
    list_per_page = 50
