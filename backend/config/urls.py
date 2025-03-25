from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from recipes.views import RecipeViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
