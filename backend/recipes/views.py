from django.db.models import Sum
from rest_framework import permissions, status, viewsets
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Recipe,
    Favorite,
    RecipeIngredient,
    Ingredient,
    Tag,
    ShoppingCart
)

from .serializers import (
    RecipeSerializer,
    RecipeMinifiedSerializer,
    IngredientSerializer,
    TagSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    GetRecipeSerializer
)
from .filters import RecipeFilter, IngredientFilter
from .permissions import AuthorOrReadOnly
from rest_framework.pagination import LimitOffsetPagination
from .utils import get_shopping_cart_textfile


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.AllowAny,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite'
    )
    def get_favorite(self, request, pk):
        """
        Добавляет или удаляет рецепт из избранного.

        Args:
            request: Запрос от клиента.
            pk: ID рецепта.

        Returns:
            Response: Ответ с данными рецепта или статусом операции.
        """
        try:
            recipe_id = int(pk)
        except ValueError:
            return Response(
                {"error": "ID рецепта должен быть целым числом."},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                RecipeMinifiedSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        else:
            if not Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {"error": "Рецепта нет в избранном."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        """
        Добавляет или удаляет рецепт из списка покупок.

        Args:
            request: Запрос от клиента.
            pk: ID рецепта.

        Returns:
            Response: Ответ с данными рецепта или статусом операции.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            if not ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {"error": "Рецепта нет в списке покупок."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Загружает список покупок в виде текстового файла.

        Args:
            request: Запрос от клиента.

        Returns:
            HttpResponse: Ответ с файлом списка покупок.
        """
        return get_shopping_cart_textfile(request.user)

    def _get_shopping_cart_ingredients(self):
        """Получает агрегированный список ингредиентов для списка покупок."""
        return RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

    def get_serializer_class(self):
        """Определяет сериализатор в зависимости от метода запроса."""
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=(permissions.AllowAny,)
    )
    def get_short_link(self, request, *args, **kwargs):
        """
        Генерирует короткую ссылку на рецепт.

        Args:
            request: Запрос от клиента.

        Returns:
            JsonResponse: Ответ с короткой ссылкой.
        """
        short_link = request.build_absolute_uri()
        short_link = short_link.replace('/api/recipes/', '/t/')
        short_link = short_link.replace('/get-link/', '/')
        return JsonResponse({'short-link': short_link})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с тегами."""

    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


def short_link_view(request, *args, **kwargs):
    """
    Перенаправляет с короткой ссылки на полный URL рецепта.

    Args:
        request: Запрос от клиента.

    Returns:
        Redirect: Перенаправление на полный URL рецепта.
    """
    path = request.build_absolute_uri()
    path = path.replace('/t/', '/api/recipes/')
    return redirect(path)
