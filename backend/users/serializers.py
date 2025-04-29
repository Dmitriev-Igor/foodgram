from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import ValidationError

from recipes.models import Recipe

from .models import Subscription

User = get_user_model()


class UsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                subscriber=request.user,
                author=obj
            ).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(
        max_length=None,
        allow_empty_file=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if not data.get('avatar'):
            raise ValidationError(
                {'avatar': 'Поле "Аватар" обязательно для заполнения!'}
            )
        return data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetSubscriptionSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes(self, obj):
        try:
            count = int(
                self.context['request'].query_params.get('recipes_limit'))
        except (TypeError, ValueError, KeyError):
            count = None

        recipes = obj.recipes.all()
        return RecipeMinifiedSerializer(
            recipes[:count],
            many=True,
            context=self.context
        ).data
