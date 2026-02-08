from rest_framework import permissions, viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from api.mixins import CreateDestroyViewSet, DestroyViewSet
from skills.models import Category, Skill, SubCategory, WantsToLearn
from skills.serializers import (
    CategorySerializer,
    ShortSkillSerializer,
    SkillImageSerializer,
    SkillSerializer,
    SubCategorySerializer,
    WantsToLearnSerializer,
)


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
