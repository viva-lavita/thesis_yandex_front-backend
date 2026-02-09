from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from api.mixins import CreateDestroyListRetrieveViewSet, CreateDestroyViewSet, DestroyViewSet
from skills.models import (
    Category,
    Skill,
    SkillExchangeNotification,
    SkillExchangeRequest,
    SkillLike,
    SubCategory,
    WantsToLearn,
)
from skills.serializers import (
    CategorySerializer,
    ShortSkillSerializer,
    SkillExchangeNotificationSerializer,
    SkillExchangeRequestCreateSerializer,
    SkillExchangeRequestSerializer,
    SkillImageSerializer,
    SkillLikeCreateSerializer,
    SkillLikeSerializer,
    SkillSerializer,
    SubCategorySerializer,
    UserFullSerializer,
    WantsToLearnSerializer,
)

User = get_user_model()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Главные категории навыков.

    Доступно всем.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Подкатегории навыков.

    Доступно всем.
    """

    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = (permissions.AllowAny,)


class SkillViewSet(viewsets.ModelViewSet):
    """
    Навыки.

    Чтение: доступно всем.
    Создание: доступно аутентифицированным пользователям.
    Обновление: доступно аутентифицированным пользователям, если они являются владельцем навыка.

    Примечание: при обновлении навыка изображения полностью перезаписываются, если передано поле image_files.
    Для точечного удаления изображений используйте роут skill-images/{id изображения}
    """

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ["retrieve", "list"]:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = ShortSkillSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="main_page", permission_classes=[permissions.AllowAny])
    def main_page(self, request, *args, **kwargs):
        """
        Получение списка пользователей для главной страницы.

        Доступ: все пользователи

        В выдаче только активные пользователи (is_active=True).
        В выдаче нет админов (!is_superuser=True).
        """
        users = User.objects.filter(is_active=True, is_superuser=False)
        return Response(UserFullSerializer(users, many=True).data)


class WantsToLearnViewSet(CreateDestroyViewSet):
    """
    Категории, навыкам из которых пользователь хочет научиться.

    Доступ: только аутентифицированным пользователям.
    """

    queryset = WantsToLearn.objects.all()
    serializer_class = WantsToLearnSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SkillImageViewSet(DestroyViewSet):
    """
    Удаление изображений навыков.

    Доступно аутентифицированным пользователям, если они являются владельцем навыка.
    """

    serializer_class = SkillImageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(skill__user=self.request.user)


class SkillExchangeRequestViewSet(CreateDestroyListRetrieveViewSet):
    """
    API для управления заявками на обмен навыками.

    Пользователь может получить только свои отправленные и полученные заявки.

    Доступно аутентифицированным пользователям.

    TODO добавить фильтры для полученных и отправленных заявок
    """

    serializer_class = SkillExchangeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SkillExchangeRequest.objects.filter(Q(requester=self.request.user) | Q(recipient=self.request.user))

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = SkillExchangeRequestCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            SkillExchangeRequestSerializer(serializer.instance).data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """Принять заявку (только для получателя)."""
        request_obj = get_object_or_404(SkillExchangeRequest, pk=pk)

        if request_obj.recipient != request.user:
            return Response({"error": "Вы не можете принять эту заявку."}, status=status.HTTP_403_FORBIDDEN)
        request_obj.accept()
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Отклонить заявку (только для получателя)."""
        request_obj = get_object_or_404(SkillExchangeRequest, pk=pk)
        if request_obj.recipient != request.user:
            return Response({"error": "Вы не можете отклонить эту заявку."}, status=status.HTTP_403_FORBIDDEN)
        request_obj.reject()
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Отменить заявку (только для инициатора)."""
        request_obj = get_object_or_404(SkillExchangeRequest, pk=pk)
        if request_obj.requester != request.user:
            return Response({"error": "Вы не можете отменить эту заявку."}, status=status.HTTP_403_FORBIDDEN)
        request_obj.cancel()
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)


class SkillLikeViewSet(CreateDestroyListRetrieveViewSet):
    """
    API для управления лайками навыков.

    Доступно аутентифицированным пользователям.
    """

    queryset = SkillLike.objects.all()
    serializer_class = SkillLikeSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).select_related("skill", "user")

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = SkillLikeCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для просмотра уведомлений.

    - Список уведомлений текущего пользователя.
    - Пометка уведомления как прочитанного.
    - Массовая пометка как прочитанное.
    """

    serializer_class = SkillExchangeNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SkillExchangeNotification.objects.filter(recipient=self.request.user).select_related(
            "request", "request__requester", "request__recipient"
        )

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """Пометить уведомление как прочитанное."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        """Пометить все уведомления как прочитанные."""
        self.get_queryset().update(is_read=True)
        return Response({"detail": "Все уведомления отмечены как прочитанные."}, status=status.HTTP_200_OK)
