from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import Q

from .constants import (
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    NAME_MAX_LENGTH,
    AVATAR_UPLOAD_PATH,
    TEXT_TRUNCATION,
)


class User(AbstractUser):
    """Кастомная модель пользователя с email в качестве username."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    email = models.EmailField(
        verbose_name='email address',
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        db_index=True,
        error_messages={'unique': 'Пользователь с таким email уже существует.'}
    )
    username = models.CharField(
        verbose_name='никнейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=NAME_MAX_LENGTH
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to=AVATAR_UPLOAD_PATH,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)  # Сортировка по логину

    def __str__(self):
        return f'{self.username} ({self.get_full_name()})'[:TEXT_TRUNCATION]


class Subscription(models.Model):
    """Модель подписки пользователей друг на друга."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_by',
        verbose_name='автор'
    )
    created = models.DateTimeField(
        verbose_name='дата подписки',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~Q(subscriber=models.F('author')),
                name='prevent_self_subscription'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} -> {self.author}'
