from django.contrib.auth import get_user_model
from djoser.serializers import UserCreatePasswordRetypeSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from api.utils import is_russian
from skills.models import SubCategory
from users.models import City

User = get_user_model()


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name"]


class UserSerializer(DjoserUserSerializer):
    """
    Базовый сериализатор пользователя для всех action кроме 'create'.

    Выводится максимальная информация о пользователе.
    """

    class Meta:
        model = User
        fields = ["pk", "email", "name", "gender", "city", "date_of_birth", "about", "avatar"]

    def validate_name(self, value):
        if not is_russian(value):
            raise serializers.ValidationError("Имя должно состоять только из русских букв")
        return value

    def validate_date_of_birth(self, value):
        if self.instance.date_of_birth and value > self.instance.date_of_birth:
            raise serializers.ValidationError("Дата рождения должна быть раньше даты регистрации")
        return value


# TODO: при патчах и путах провалидировать, что имя, гендер, дата рождения и город не обнуляются(в бд можно null)
class CustomSubCategorySerializer(serializers.Serializer):
    subcategory = subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())

    class Meta:
        fields = ["subcategory"]


class UserCreateSerializer(DjoserUserCreateSerializer):
    """
    Сериализатор создания пользователя.
    """

    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), write_only=True)
    gender = serializers.ChoiceField(choices=User.Gender.choices, write_only=True)
    wants_to_learn = CustomSubCategorySerializer(many=True, write_only=True, required=False)

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
            "about",
            "avatar",
            "wants_to_learn",
        )
        extra_kwargs = {
            "about": {"required": False},
            "avatar": {"required": False},
            "name": {"required": True},
            "date_of_birth": {"required": True},
            "gender": {"required": True},
            "city": {"required": True},
            "wants_to_learn": {"required": False},
        }

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

    # def validate_wants_to_learn(self, value):
    #     if isinstance(value, str):
    #         try:
    #             data = json.loads(value)
    #             # Проверяем, что это список
    #             if not isinstance(data, list):
    #                 raise serializers.ValidationError("wants_to_learn должен быть списком")
    #             return data
    #         except json.JSONDecodeError:
    #             raise serializers.ValidationError("Некорректный JSON в wants_to_learn")
    #     return value  # если уже список (например, из теста)

    # def validate(self, attrs):
    #     print(attrs)
    #     # wants_to_learn = attrs.pop("wants_to_learn")
    #     wants_to_learn = attrs.pop("wants_to_learn", None)
    #     if wants_to_learn:
    #         for want in wants_to_learn:
    #             WantsToLearn(user=self.instance, subcategory=want["subcategory"]).save()
    #     return super().validate(attrs)


class ShortReadUserSerializer(serializers.ModelSerializer):
    # TODO: добавить поля: может научить, хочет научиться
    class Meta:
        model = User
        fields = ("id", "name", "city", "date_of_birth", "gender", "about", "avatar")


class UserDeleteSerializer(serializers.Serializer):
    """
    Сериализатор удаления пользователя.

    Переопределено, т.к. Djoser по дефолту просит текущий пароль
    в теле запроса, что не поддерживается (и не одобряется) OpenAPI.
    """

    pass
