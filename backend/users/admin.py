from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import Subscription

User = get_user_model()


@admin.register(User)
class UsersAdmin(BaseUserAdmin):
    """Админ-панель для модели User."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'avatar_preview',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'avatar')}),
        ('Права', {'fields': ('is_active', 'is_staff',
                              'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')

    @admin.display(description="Аватар")  # Используем декоратор для описания
    def avatar_preview(self, obj):
        """Отображает миниатюру аватара в админ-панели."""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" />',
                obj.avatar.url
            )
        return "Нет аватара"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для модели Subscription."""

    list_display = ('subscriber', 'author', 'created')
    list_filter = ('created',)
    search_fields = (
        'subscriber__username',
        'author__username',
        'subscriber__email',
        'author__email'
    )
    raw_id_fields = ('subscriber', 'author')
