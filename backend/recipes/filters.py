from django_filters import rest_framework as filters
from django_filters import CharFilter
from .models import Recipe, Tag, Ingredient


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=True,
        label='Теги (полное совпадение)'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        label='В избранном'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='В корзине'
    )
    recipes_limit = filters.NumberFilter(
        method='filter_recipes_limit',
        label='Лимит рецептов'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'recipes_limit')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        return queryset.filter(favorites__user=user) if value else queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        return queryset.filter(shopping_carts__user=user) if value else queryset

    def filter_recipes_limit(self, queryset, name, value):
        try:
            return queryset[:int(value)]
        except (TypeError, ValueError):
            return queryset


class IngredientFilter(filters.FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        label='Поиск по началу названия'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
