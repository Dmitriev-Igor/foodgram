from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from .models import Ingredient
from .serializers import IngredientSerializer

class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')
    
    class Meta:
        model = Ingredient
        fields = ('name',)

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter