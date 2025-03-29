from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Recipe, ShoppingCart, Favorite, RecipeIngredient
from .serializers import RecipeSerializer, RecipeMinifiedSerializer
from .filters import RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_class = RecipeFilter

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            _, created = Favorite.objects.get_or_create(
                user=request.user, recipe=recipe)
            if not created:
                return Response({'error': 'Рецепт уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
            # Используем сокращенный сериализатор
            serializer = RecipeMinifiedSerializer(instance=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        recipes_limit = request.query_params.get('recipes_limit')
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        if recipes_limit:
            ingredients = ingredients[:int(recipes_limit)]

    def generate_pdf_response(self, ingredients):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        y = 800
        for ing in ingredients:
            p.drawString(
                100,
                y,
                f"{ing['ingredient__name']} ({ing['ingredient__measurement_unit']}) - {ing['total']}"
            )
            y -= 20
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
