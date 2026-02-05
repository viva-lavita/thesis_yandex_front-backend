from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class City(models.Model):
    name = models.CharField(
        verbose_name="Город",
        max_length=50,
        unique=True,
        help_text="Не более 50 символов.",
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):  # TODO вынести в UserInfo все неважные поля(OneToOne)
    class Gender(models.TextChoices):
        MALE = "male", "Мужской"
        FEMALE = "female", "Женский"

    name = models.CharField(
        verbose_name="Имя",
        max_length=100,
        blank=True,
        null=True,
        help_text="Не более 50 символов.",
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата рождения",
    )
    gender = models.CharField(
        verbose_name="Пол",
        max_length=6,
        choices=Gender.choices,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        verbose_name="Email",
        max_length=254,
        unique=True,
        db_index=True,
        help_text="Не более 254 символов. Только буквы, цифры и @/./+/-/_.",
        error_messages={
            "unique": "Пользователь с таким email уже существует.",
            "invalid": "Некорректный email.",
            "max_length": "Email слишком длинный.",
        },
    )
    city = models.ForeignKey(
        City,
        related_name="users",
        verbose_name="Город",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата обновления",
        auto_now=True,
    )

    USERNAME_FIELD = "email"  # переопределение поля для логина
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def username(self):
        """Поле username упразднено из модели, но необходимо для работы."""
        return self.get_username()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.name} {self.pk}"
