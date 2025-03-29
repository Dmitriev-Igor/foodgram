from rest_framework import serializers
from .models import Recipe, Tag, Ingredient, RecipeIngredient, ShoppingCart, Favorite
from users.serializers import UserSerializer
from drf_spectacular.utils import extend_schema_field


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        required=True
    )
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    # Возвращает URI вместо Base64
    image = serializers.ImageField(use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'cooking_time', 'image',
            'tags', 'ingredients', 'author', 'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = ('author',)

    @extend_schema_field(serializers.BooleanField)
    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.in_favorites.filter(user=user).exists()

    @extend_schema_field(serializers.BooleanField)
    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.in_shopping_carts.filter(user=user).exists()

    def create(self, validated_data):
        ingredients_data = self.initial_data.get('ingredients', [])
        tags_ids = self.initial_data.get('tags', [])
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags_ids)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = self.initial_data.get('ingredients', [])
        tags_ids = self.initial_data.get('tags', [])

        instance = super().update(instance, validated_data)
        instance.tags.set(tags_ids)
        instance.recipe_ingredients.all().delete()

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
