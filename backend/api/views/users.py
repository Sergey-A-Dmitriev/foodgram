from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from api.serializers.users import (AvatarSerializer,
                                   SubscriptionAuthorSerializer)
from recipes.models import Subscription

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """ViewSet для кастомной модели User."""

    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_field = 'pk'

    def get_queryset(self):
        return User.objects.annotate(
            recipes_count=Count('recipes'))

    @extend_schema(exclude=True)
    @action(methods=['post'],
            detail=False,
            url_path='activation',
            url_name='activation')
    def activation(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(exclude=True)
    @action(methods=['post'],
            detail=False,
            url_path='resend_activation',
            url_name='resend_activation')
    def resend_activation(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(exclude=True)
    @action(methods=['post'],
            detail=False,
            url_path='reset_email',
            url_name='reset_email')
    def reset_email(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(exclude=True)
    @action(methods=['post'],
            detail=False,
            url_path='reset_email_confirm',
            url_name='reset_email_confirm')
    def reset_email_confirm(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @extend_schema(exclude=True)
    @action(methods=['post'],
            detail=False,
            url_path='reset_password',
            url_name='reset_password')
    def reset_password(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @extend_schema(exclude=True)
    @action(methods=['post'],
            detail=False,
            url_path='reset_password_confirm',
            url_name='reset_password_confirm')
    def reset_password_confirm(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(exclude=True)
    @action(methods=['post'],
            detail=False,
            url_path='set_email',
            url_name='set_email')
    def set_email(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'subscriptions':
            return SubscriptionAuthorSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        return super().get_serializer_class()

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def me(self, request):
        """Метод для me/ (GET)."""
        return super().me(request)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Метод для получения подписок (GET)."""
        return self.get_paginated_response(
            SubscriptionAuthorSerializer(
                self.paginate_queryset(
                    User.objects.filter(
                        subscriptions_as_author__user=request.user)),
                many=True,
                context={'request': request}).data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписка / отписка на автора."""

        user = request.user
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author_id=pk)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        author = get_object_or_404(User, pk=pk)
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя')
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            author=author)
        if not created:
            raise ValidationError(
                f'Уже подписаны на {author.username}')
        serializer = SubscriptionAuthorSerializer(
            author,
            context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAuthenticated])
    def avatar(self, request):

        if request.method == 'PUT':
            serializer = AvatarSerializer(
                request.user,
                data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = request.user
        user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
