from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    """Категория навыка"""

    name = models.CharField(max_length=50, unique=True, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория навыка"
        verbose_name_plural = "Категории навыков"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """Подкатегория навыка"""

    name = models.CharField(max_length=50, unique=True, verbose_name="Название подкатегории")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories", verbose_name="Категория"
    )

    class Meta:
        verbose_name = "Подкатегория навыка"
        verbose_name_plural = "Подкатегории навыков"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Навык"""

    name = models.CharField(
        max_length=100,
        verbose_name="Название навыка",
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, related_name="skills", verbose_name="Подкатегория"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills", verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["-pk"]

    def __str__(self):
        return self.name
