from django.contrib.auth import get_user_model
from djoser.serializers import UserCreatePasswordRetypeSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from api.utils import is_russian

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    """
    Базовый сериализатор пользователя для всех action кроме 'create'.

    Выводится максимальная информация о пользователе.
    """

    class Meta:
        model = User
        fields = ["pk", "email", "name", "gender", "city", "date_of_birth"]

    def validate_name(self, value):
        if not is_russian(value):
            raise serializers.ValidationError("Имя должно состоять только из русских букв")
        return value

    def validate_date_of_birth(self, value):
        if not value:
            raise serializers.ValidationError("Дата рождения не может быть пустой")
        if self.instance.date_of_birth and value > self.instance.date_of_birth:
            raise serializers.ValidationError("Дата рождения должна быть раньше даты регистрации")
        return value


class UserCreateSerializer(DjoserUserCreateSerializer):
    """
    Сериализатор создания пользователя.
    """

    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "re_password",
            "name",
            "gender",
            "city",
            "date_of_birth",
        )
        extra_kwargs = {"gender": {"required": False}}

    def validate_name(self, value):
        if not is_russian(value):
            raise serializers.ValidationError("Имя должно состоять только из русских букв")
        return value

    def validate_date_of_birth(self, value):
        if not value:
            raise serializers.ValidationError("Дата рождения не может быть пустой")
        if self.instance and self.instance.date_of_birth and value > self.instance.date_of_birth:
            raise serializers.ValidationError("Дата рождения должна быть раньше даты регистрации")
        return value


class ShortReadUserSerializer(serializers.ModelSerializer):
    child = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "name", "email")


class UserDeleteSerializer(serializers.Serializer):
    """
    Сериализатор удаления пользователя.

    Переопределено, т.к. Djoser по дефолту просит текущий пароль
    в теле запроса, что не поддерживается (и не одобряется) OpenAPI.
    """

    pass
