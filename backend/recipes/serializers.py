from django.db import transaction
from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError)
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UsersSerializer
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UsersSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set'
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            obj.recipeingredient_set.all(),
            many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.shopping_carts.filter(user=request.user).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name', 'author',
                  'image', 'text', 'cooking_time')

    def validate(self, data):
        errors = {}

        if not data.get('image'):
            errors['image'] = 'Обязательное поле'

        tags = data.get('tags', [])
        if not tags:
            errors['tags'] = 'Необходим хотя бы один тег'
        elif len(tags) != len(set(tags)):
            errors['tags'] = 'Теги не должны повторяться'

        ingredients = data.get('ingredients', [])
        if not ingredients:
            errors['ingredients'] = 'Необходим хотя бы один ингредиент'
        else:
            ingredient_ids = {ing['id'].id for ing in ingredients}
            if len(ingredient_ids) != len(ingredients):
                errors['ingredients'] = 'Ингредиенты не должны повторяться'

        if errors:
            raise ValidationError(errors)

        return data

    def _add_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = super().create(validated_data)

        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')

        if tags:
            instance.tags.set(tags)

        if ingredients:
            instance.ingredients.clear()
            self._add_ingredients(instance, ingredients)

        return instance

    def to_representation(self, instance):
        return GetRecipeSerializer(instance, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке покупок'
            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном'
            )
        ]
