from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now

from skills.utils import skill_image_upload_path

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
    """Навыки, которым может научить пользователь."""

    name = models.CharField(
        max_length=100,
        verbose_name="Название навыка",
    )
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, related_name="skills", verbose_name="Подкатегория"
    )
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name="Описание")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills", verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["-pk"]

    def __str__(self):
        return self.name


class SkillImage(models.Model):
    """Изображение навыка."""

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="images", verbose_name="Навык")
    image = models.ImageField(upload_to=skill_image_upload_path, verbose_name="Изображение")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    def __str__(self):
        return f"Изображение {self.pk} - {self.skill.name}"


class WantsToLearn(models.Model):
    """
    Категории, навыкам из которых хочет научиться.

    Отдельная модель -> удобнее расширять.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wants_to_learn", verbose_name="Пользователь")
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, related_name="wants_to_learn", verbose_name="Подкатегория"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "subcategory")
        verbose_name = "Хочет научиться"
        verbose_name_plural = "Хотят научиться"

    def __str__(self):
        return f"{self.user} хочет научиться в {self.subcategory})"


class SkillExchangeRequest(models.Model):
    """
    Заявка на обмен навыками между пользователями.

    Один пользователь предлагает свой навык в обмен на навык из определённой подкатегории.
    """

    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exchange_requests_sent", verbose_name="Инициатор обмена"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exchange_requests_received", verbose_name="Получатель предложения"
    )
    # Статус заявки
    STATUS_CHOICES = [
        ("pending", "Ожидает рассмотрения"),
        ("accepted", "Принята"),
        ("rejected", "Отклонена"),
        ("cancelled", "Отменена инициатором"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус заявки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    responded_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата ответа")

    class Meta:
        verbose_name = "Заявка на обмен навыками"
        verbose_name_plural = "Заявки на обмен навыками"
        unique_together = ("requester", "recipient")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.requester} → {self.recipient}"

    def accept(self):
        """Принять заявку."""
        self.status = "accepted"
        self.responded_at = now()
        self.save()

    def reject(self):
        """Отклонить заявку."""
        self.status = "rejected"
        self.responded_at = now()
        self.save()

    def cancel(self):
        """Отменить заявку (инициатором)."""
        self.status = "cancelled"
        self.responded_at = now()
        self.save()


# TODO Избранное/Лайки - ManyToMany отдельная таблица, кто, кого, дата?
# TODO Уведомления? принял обмен, предлагает обмен, просмотрено-нет,
