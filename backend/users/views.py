import json
import re

from django.db import transaction
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from skills.models import WantsToLearn
from users.models import City
from users.serializers import CityListSerializer, CitySerializer, UserCreateSerializer


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "list":
            self.serializer_class = CityListSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer({"cities": queryset})
        return Response(serializer.data)


class UserViewSet(DjoserUserViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        """
        Доступ только для авторизованных пользователей.

        Пользователь может получить только свой профиль.
        Любой профиль может посмотреть только админ.
        """
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Доступ только для авторизованных пользователей.

        Любой профиль может посмотреть только админ.
        Авторизованный пользователь может посмотреть свой профиль.
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Доступ только для неавторизованных пользователей."""
        serializer = UserCreateSerializer(data=request.data)
        wants_to_learn_data = request.data.get("wants_to_learn", None)
        with transaction.atomic():
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                if wants_to_learn_data:
                    if isinstance(wants_to_learn_data, str):
                        cleaned = re.sub(r"\s+", "", wants_to_learn_data)
                        if not cleaned.startswith("["):
                            cleaned = f"[{cleaned}]"
                        wants_to_learn_data = json.loads(cleaned)
                    for want in wants_to_learn_data:
                        # TODO добавить проверку id субкатегорий на существование
                        WantsToLearn(user=serializer.instance, subcategory_id=want["subcategory"]).save()
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Доступ только для авторизованных пользователей.

        Пользователь может обновить свой профиль.
        Любой профиль может обновить только админ.
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Доступ только для авторизованных пользователей.

        Пользователь может обновить свой профиль.
        Любой профиль может обновить только админ.
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Доступ только для авторизованных пользователей.

        Пользователь может удалить свой профиль.
        Любой профиль может удалить только админ.
        """
        # частично переопределено, т.к. требовался текущий пароль в теле запроса
        # тело при delete методе не одобряется OpenAPI
        if request.user.is_superuser or int(self.kwargs["id"]) == request.user.id:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
