from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.serializers.users import (AvatarSerializer, SetPasswordSerializer,
                                   SubscriptionSerializer,
                                   UserCreateSerializer, UserSerializer)
from users.models import Subscription

User = get_user_model()


class UserViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin,
                  GenericViewSet):
    """ViewSet для кастомной модели User."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'me':
            return UserSerializer
        if self.action == 'subscriptions':
            return SubscriptionSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        return UserSerializer

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def me(self, request):
        """Метод для me/ (GET)."""
        serializer = self.get_serializer(
            request.user)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Метод для получения подписок (GET)."""
        authors = User.objects.filter(
            subscribers__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Метод для создания и удаления подписки (POST, DELETE)."""
        author = self.get_object()
        user = request.user
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                return Response(
                    {'errors': 'Уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(
                user=user,
                author=author)
            serializer = SubscriptionSerializer(
                author,
                context={'request': request})

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(
            user=user,
            author=author)
        if not subscription.exists():
            return Response(
                {'errors': 'Подписки нет на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Метод для добавления/удаления аватара."""
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                request.user,
                data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            request.user.avatar.delete()
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def set_password(self, request):
        """Метод для изменения пароля."""
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(
            serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
