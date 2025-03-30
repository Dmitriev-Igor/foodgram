from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

# Импорты ViewSets
from recipes.views import RecipeViewSet, IngredientViewSet
from users.views import UserViewSet

router = DefaultRouter()

# Регистрация ViewSets
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    # API endpoints
    path('api/', include((router.urls, 'api'), namespace='api')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'api/schema/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
]

# Добавляем админку и медиа-файлы только в DEV-режиме
if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    ]
