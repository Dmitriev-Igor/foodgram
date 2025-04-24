from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.permissions import AnonimOrAuthenticatedReadOnly
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import (
    AvatarSerializer,
    CustomSetPasswordSerializer,
    GetSubscriptionSerializer,
    MyUserSerializer,
)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (AnonimOrAuthenticatedReadOnly,)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_me(self, request):
        if request.method == 'PATCH':
            serializer = MyUserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = MyUserSerializer(
            request.user,
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = CustomSetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_avatar(self, request):
        user = request.user

        if request.method == 'DELETE':
            if not user.avatar:
                return Response(
                    {'error': 'Аватар отсутствует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.avatar.delete()
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(
            user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Subscription.objects.filter(
                    subscriber=request.user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Subscription.objects.create(subscriber=request.user, author=author)
            serializer = GetSubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE метод
        subscription = Subscription.objects.filter(
            subscriber=request.user,
            author=author
        ).first()

        if not subscription:
            return Response(
                {'errors': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            subscribed_by__subscriber=request.user
        )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subscriptions, request)

        serializer = GetSubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
