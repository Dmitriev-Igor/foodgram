from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeMinifiedSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .utils import get_shopping_cart_textfile


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.AllowAny,)
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def _handle_object_creation(self,
                                request,
                                pk,
                                serializer_class,
                                error_message):
        """Общий метод для создания объектов (избранное/корзина)."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            RecipeMinifiedSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def _handle_object_deletion(self, request, pk, model_class, error_message):
        """Общий метод для удаления объектов (избранное/корзина)."""
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted_count, _ = model_class.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()

        if deleted_count == 0:
            return Response(
                {"error": error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='favorite')
    def add_favorite(self, request, pk):
        """Добавление рецепта в избранное."""
        return self._handle_object_creation(
            request,
            pk,
            FavoriteSerializer,
            "Рецепт уже в избранном"
        )

    @add_favorite.mapping.delete
    def remove_favorite(self, request, pk):
        """Удаление рецепта из избранного."""
        return self._handle_object_deletion(
            request,
            pk,
            Favorite,
            "Рецепта нет в избранном"
        )

    @action(detail=True, methods=['post'], url_path='shopping_cart')
    def add_shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок."""
        return self._handle_object_creation(
            request,
            pk,
            ShoppingCartSerializer,
            "Рецепт уже в списке покупок"
        )

    @add_shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk):
        """Удаление рецепта из списка покупок."""
        return self._handle_object_deletion(
            request,
            pk,
            ShoppingCart,
            "Рецепта нет в списке покупок"
        )

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Загрузка списка покупок."""
        return get_shopping_cart_textfile(request.user)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=(permissions.AllowAny,)
    )
    def get_short_link(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        relative_link = f'/api/recipes/{recipe_id}/get-link/'
        short_link = request.build_absolute_uri(relative_link)
        short_link = short_link.replace('/api/recipes/', '/t/')
        short_link = short_link.replace('/get-link/', '/')

        return JsonResponse({'short-link': short_link})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


def short_link_view(request, *args, **kwargs):
    recipe_id = kwargs.get('recipe_id')

    try:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        path = f'/recipes/{recipe.id}/'
        return redirect(path)

    except Http404:
        return redirect('/404/')
