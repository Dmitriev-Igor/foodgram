from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


LENGTH_TEXT = 20


class User(AbstractUser):
    """Кастомная модель пользователя с email в качестве username."""
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password',)

    email = models.EmailField(
        'email address',
        unique=True,
        max_length=254,
        db_index=True,
        error_messages={
            'unique': 'Пользователь с таким email уже существует.'
        }
    )
    username = models.CharField(
        verbose_name='никнейм',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField('Пароль', max_length=150)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]

    def __str__(self):
        return f'{self.username} ({self.get_full_name()})'[:LENGTH_TEXT]


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
    created = models.DateTimeField('дата подписки', auto_now_add=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.subscriber} -> {self.author}'