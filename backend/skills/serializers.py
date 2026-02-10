from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from skills.models import (
    Category,
    Skill,
    SkillExchangeNotification,
    SkillExchangeRequest,
    SkillImage,
    SkillLike,
    SubCategory,
    WantsToLearn,
)
from skills.services import create_skill_with_images
from users.serializers import CitySerializer, ShortReadUserSerializer

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор главной категории навыков."""

    class Meta:
        model = Category
        fields = "__all__"


class CategoryListSerializer(serializers.Serializer):
    categories = CategorySerializer(many=True)

    class Meta:
        fields = ["categories"]


class SubCategorySerializer(serializers.ModelSerializer):
    """Сериализатор подкатегории навыков."""

    category = CategorySerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = ["id", "name", "category"]


class SubCategoryListSerializer(serializers.Serializer):
    subcategories = SubCategorySerializer(many=True)

    class Meta:
        fields = ["subcategories"]


class SkillImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillImage
        fields = ["id", "image", "uploaded_at"]
        read_only_fields = ["uploaded_at"]


class SkillSerializer(serializers.ModelSerializer):
    images = SkillImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )  # селект релейтед
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), write_only=True)
    user = ShortReadUserSerializer(read_only=True)
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "description",
            "images",
            "image_files",
            "subcategory",
            "user",
            "subcategory_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "user"]
        # images — для чтения
        # image_files — для записи

    def validate_image_files(self, value):
        if not value:
            return value
        for image in value:
            if image.size > 5 * 1024 * 1024:  # 5 МБ
                raise serializers.ValidationError("Файл слишком большой (максимум 5 МБ).")
            if not image.content_type.startswith("image/"):
                raise serializers.ValidationError("Только изображения (jpg, png и т.д.).")
        return value

    def create(self, validated_data):
        image_files = validated_data.pop("image_files", [])
        return create_skill_with_images(validated_data=validated_data, image_files=image_files)

    def update(self, instance, validated_data):
        with transaction.atomic():
            if "image_files" in validated_data:
                self.validate_image_files(validated_data["image_files"])
                image_files = validated_data.pop("image_files")
                instance.images.all().delete()
                try:
                    images = [SkillImage(skill=instance, image=file) for file in image_files]
                    SkillImage.objects.bulk_create(images)
                except Exception as e:
                    raise serializers.ValidationError(f"Ошибка загрузки изображений: {e}")
            return super().update(instance, validated_data)


# для выдачи в списке
class ShortSkillSerializer(serializers.ModelSerializer):
    images = SkillImageSerializer(many=True, read_only=True)
    subcategory = SubCategorySerializer(read_only=True)

    class Meta:
        model = Skill
        fields = ["id", "name", "images", "subcategory"]


class WantsToLearnSerializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())

    class Meta:
        model = WantsToLearn
        fields = ["subcategory", "subcategory_name", "created_at"]
        read_only_fields = ["created_at", "subcategory_name"]


class SkillExchangeRequestCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания заявки на обмен."""

    class Meta:
        model = SkillExchangeRequest
        fields = ["recipient"]

    def validate(self, data):
        # Запрет отправки заявки самому себе
        if self.context["request"].user == data["recipient"]:
            raise serializers.ValidationError("Нельзя отправить заявку самому себе.")
        if SkillExchangeRequest.objects.filter(
            requester=self.context["request"].user, recipient=data["recipient"]
        ).exists():
            raise serializers.ValidationError("Вы уже отправили заявку на обмен с этим пользователем.")
        return data


class SkillExchangeRequestSerializer(serializers.ModelSerializer):
    """Сериализатор заявки на обмен."""

    recipient_full_name = serializers.CharField(source="recipient.get_full_name", read_only=True)

    class Meta:
        model = SkillExchangeRequest
        fields = [
            "id",
            "recipient",
            "recipient_full_name",
            "status",
            "created_at",
            "responded_at",
        ]
        read_only_fields = ["created_at", "responded_at", "status", "recipient"]


class SkillLikeCreateSerializer(serializers.ModelSerializer):
    skill = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all())

    class Meta:
        model = SkillLike
        fields = ["id", "skill"]

    def validate(self, attrs):
        if SkillLike.objects.filter(user=self.context["request"].user, skill=attrs["skill"]).exists():
            raise serializers.ValidationError("Вы уже поставили лайк на этот навык.")
        if attrs["skill"].user == self.context["request"].user:
            raise serializers.ValidationError("Нельзя поставить лайк на свой навык.")
        return super().validate(attrs)


class SkillLikeSerializer(serializers.ModelSerializer):
    """Сериализатор лайка навыка. Только для чтения."""

    skill = ShortSkillSerializer(read_only=True)
    user = ShortReadUserSerializer(read_only=True)

    class Meta:
        model = SkillLike
        fields = ["id", "user", "skill", "created_at"]
        read_only_fields = ["id", "user", "skill", "created_at"]


class SkillExchangeNotificationSerializer(serializers.ModelSerializer):
    request_id = serializers.IntegerField(source="request.id", read_only=True)
    recipient_name = serializers.CharField(source="request.recipient.get_full_name", read_only=True)

    class Meta:
        model = SkillExchangeNotification
        fields = ["id", "request_id", "recipient_name", "event_type", "is_read", "created_at"]
        read_only_fields = ["created_at", "request_id", "recipient_name", "event_type", "is_read"]


class UserFullSerializer(ShortReadUserSerializer):
    skills = ShortSkillSerializer(many=True, read_only=True)
    wants_to_learn = WantsToLearnSerializer(many=True, read_only=True)
    age = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    city = CitySerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "city",
            "gender",
            "avatar",
            "skills",
            "wants_to_learn",
            "age",
            "is_liked",
            "likes_count",
        )

    def get_age(self, obj):
        if obj.date_of_birth:
            return obj.get_age()
        return None

    def get_is_liked(self, obj):
        return SkillLike.objects.filter(user=self.context["request"].user, skill__user=obj).exists()

    def get_likes_count(self, obj):
        return SkillLike.objects.filter(skill__user=obj).count()
