from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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


class User(AbstractUser):
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=50,
        blank=True,
        null=True,
        help_text="Не более 50 символов.",
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=50,
        blank=True,
        null=True,
        help_text="Не более 50 символов.",
    )
    patronymic_name = models.CharField(
        verbose_name="Отчество",
        max_length=50,
        blank=True,
        null=True,
        help_text=" более 50 символов.",
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата рождения",
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
    post = models.CharField(
        verbose_name="Должность",
        max_length=70,
        blank=True,
        null=True,
        help_text="Не более 50 символов.",
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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
