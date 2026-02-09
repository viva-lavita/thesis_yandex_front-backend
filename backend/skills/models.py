from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ValidationError
from django.utils.timezone import now

from skills.utils import skill_image_upload_path

User = get_user_model()


class Category(models.Model):
    """Категория навыка"""

    name = models.CharField(max_length=50, unique=True, verbose_name="Название категории")
    color = models.CharField(max_length=50, unique=True, default="#42CAD1", verbose_name="Цвет категории")

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


class SkillLike(models.Model):
    """
    Модель для хранения лайков/избранных навыков пользователя.

    Позволяет:
    - отмечать навыки как «понравившиеся»;
    - отслеживать, кто и когда поставил лайк;
    - избегать дублирования (один пользователь — один лайк на навык).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_skills", verbose_name="Пользователь")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="likes", verbose_name="Навык")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления в избранное")

    class Meta:
        verbose_name = "Лайк навыка"
        verbose_name_plural = "Лайки навыков"
        unique_together = ("user", "skill")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} лайкнул {self.skill}"

    def save(self, *args, **kwargs):
        if SkillLike.objects.filter(user=self.user, skill=self.skill).exists():
            raise ValidationError("Вы уже лайкнули этот навык.")
        super().save(*args, **kwargs)

    @classmethod
    def toggle_like(cls, user, skill):
        """
        Добавить/убрать лайк. Возвращает True, если лайк добавлен, False — если удалён.
        """
        try:
            cls.objects.create(user=user, skill=skill)
            return True
        except ValidationError:
            cls.objects.filter(user=user, skill=skill).delete()
            return False


class SkillExchangeNotification(models.Model):
    """
    Уведомление о событиях, связанных с заявками на обмен навыками.

    События:
    - Новая заявка (отправитель → получатель)
    - Заявка принята (получатель → отправитель)
    - Заявка отклонена (получатель → отправитель)
    - Заявка отменена (отправитель → получатель)
    """

    request = models.ForeignKey(
        SkillExchangeRequest, on_delete=models.CASCADE, related_name="notifications", verbose_name="Заявка"
    )
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Получатель уведомления")
    EVENT_CHOICES = [
        ("new_request", "Новая заявка на обмен"),
        ("accepted", "Заявка принята"),
        ("rejected", "Заявка отклонена"),
        ("cancelled", "Заявка отменена"),
    ]
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, verbose_name="Тип события")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Уведомление об обмене навыками"
        verbose_name_plural = "Уведомления об обмене навыками"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} для {self.recipient}"
