from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from recipes.constants import (SIZE_EMAIL_FIELD, SIZE_FIRSTNAME_FIELD,
                               SIZE_LASTNAME_FIELD, SIZE_TEXT_FIELD,
                               SIZE_USERNAME_FIELD)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты',
        max_length=SIZE_EMAIL_FIELD)
    username = models.CharField(
        max_length=SIZE_USERNAME_FIELD,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='Уникальный юзернейм')
    first_name = models.CharField(
        max_length=SIZE_FIRSTNAME_FIELD,
        verbose_name='Имя')
    last_name = models.CharField(
        max_length=SIZE_LASTNAME_FIELD,
        verbose_name='Фамилия')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Ссылка на аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        """Служебный класс."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        """Магический метод __str__."""
        return self.username[:SIZE_TEXT_FIELD]


class Subscription(models.Model):
    """Модель Подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор')

    class Meta:
        """Служебный класс."""

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'),

            models.CheckConstraint(
                condition=~models.Q(user=models.F('author')),
                name='prevent_self_subscription')]

        indexes = [models.Index(fields=['user']),
                   models.Index(fields=['author']),]

    def __str__(self):
        """Магический метод __str__."""
        return f'{self.user} подписан на {self.author}'[:SIZE_TEXT_FIELD]
