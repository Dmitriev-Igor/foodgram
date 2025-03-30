from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from io import BytesIO
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ingredient
from .serializers import IngredientSerializer
from .filters import IngredientFilter
from .models import Recipe, Favorite, RecipeIngredient
from .serializers import RecipeSerializer, RecipeMinifiedSerializer
from .filters import RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('author').prefetch_related(
            'tags',
            'recipe_ingredients__ingredient',
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        exists = Favorite.objects.filter(
            user=request.user,
            recipe_id=pk
        ).exists()

        if request.method == 'POST':
            if exists:
                return Response(
                    {'error': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Favorite.objects.create(user=request.user, recipe_id=pk)
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = RecipeMinifiedSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if exists:
            Favorite.objects.filter(user=request.user, recipe_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).select_related('ingredient').values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        if self.request.query_params.get('recipes_limit'):
            ingredients = ingredients[:int(
                self.request.query_params.get('recipes_limit'))]

        return self.generate_pdf_response(ingredients)

    def generate_pdf_response(self, ingredients):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        y = 800

        p.drawString(100, y, "Список покупок:")
        y -= 30

        for ing in ingredients:
            text = (
                f"{ing['ingredient__name']} "
                f"({ing['ingredient__measurement_unit']}) - "
                f"{ing['total']}"
            )
            p.drawString(100, y, text)
            y -= 20

        p.save()
        buffer.seek(0)
        response = HttpResponse(
            buffer,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
