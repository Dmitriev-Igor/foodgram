from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.http import HttpResponse
from .models import Recipe, ShoppingCart
from .serializers import RecipeSerializer
from reportlab.pdfgen import canvas
from io import BytesIO


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            _, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if not created:
                return Response(
                    {'error': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_201_CREATED)

        ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        content = '\n'.join(
            f"{ing['ingredient__name']} ({ing['ingredient__measurement_unit']}) - {ing['total']}"
            for ing in ingredients
        )
        return HttpResponse(content, content_type='text/plain')

    def generate_pdf(self, ingredients):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        y = 800
        for ing in ingredients:
            p.drawString(
                100, y, f"{ing['name']} ({ing['unit']}) - {ing['amount']}")
            y -= 20
        p.save()
        return buffer.getvalue()
