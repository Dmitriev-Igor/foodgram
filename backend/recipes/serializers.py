from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    ValidationError
)
from rest_framework.validators import UniqueTogetherValidator
from .models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    ShoppingCart,
    Favorite,
)
from users.serializers import MyUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import NotAuthenticated


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
    author = MyUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
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

    @staticmethod
    def get_ingredients(object):
        ingredients = RecipeIngredient.objects.filter(recipe=object)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.favorites.filter(
            recipe=obj).exists() if user.is_authenticated else False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return user.shopping_carts.filter(
            recipe=obj).exists() if user.is_authenticated else False


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)

    def validate(self, data):
        if not data.get('image'):
            raise ValidationError(
                {'image': 'Отсутствует поле image"!'}
            )
        return data

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError(
                {'ingredients':
                 'Не выбрано ни одного ингредиента!'}
            )
        ingredients_data = [ingredient['id'].id for ingredient in ingredients]
        if len(ingredients_data) != len(set(ingredients_data)):
            raise ValidationError(
                {'ingredients':
                 'Ингредиенты в рецепте не должны повторяться!'}
            )
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise ValidationError(
                    {'amount':
                     'Количество ингредиента должно быть больше 0!'}
                )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError(
                {'tags': 'Не выбрано ни одного тега!'})
        if len(tags) != len(set(tags)):
            raise ValidationError(
                {'tags': 'Теги рецепта не должны повторяться!'}
            )
        return tags

    def add_fields(self, ingredients, tags, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
        recipe.tags.set(tags)

    def create(self, validated_data):
        request = self.context.get('request')

        if request is None or request.user.is_anonymous:
            raise NotAuthenticated(
                detail="Authentication credentials were not provided.",
                code='not_authenticated'
            )
        user = self.context['request'].user
        validated_data['author'] = user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.add_fields(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags_data = validated_data.get('tags')
        if not tags_data:
            raise ValidationError(
                {'tags': 'Не выбрано ни одного тега!'})
        instance.tags.clear()
        instance.tags.set(tags_data)
        ingredients_data = validated_data.get('ingredients')
        if not ingredients_data:
            raise ValidationError(
                {'ingredients':
                 'Не выбрано ни одного ингредиента!'}
            )
        instance.ingredients.clear()
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        ])
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = GetRecipeSerializer(instance, context=self.context)
        return serializer.data


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
