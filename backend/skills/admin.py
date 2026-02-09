from pyexpat.errors import messages

from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html
from django.utils.timezone import now

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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = (
        "id",
        "name",
    )


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category__name")
    search_fields = (
        "id",
        "name",
        "category__name",
    )


class SkillImageInline(admin.TabularInline):
    model = SkillImage
    extra = 1


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "subcategory_name", "user_name", "created_at", "updated_at")
    search_fields = ("id", "name", "subcategory__name", "user__name")
    inlines = (SkillImageInline,)

    @admin.display(description="Подкатегория")
    def subcategory_name(self, obj):
        return obj.subcategory.name

    @admin.display(description="Пользователь")
    def user_name(self, obj):
        return obj.user.name


@admin.register(SkillExchangeRequest)
class SkillExchangeRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "requester",
        "recipient",
        "status",
        "created_at",
        "responded_at",
        "action_buttons",
    ]
    list_filter = [
        "status",
        "created_at",
    ]
    search_fields = [
        "requester__username",
        "recipient__username",
    ]

    # Поля, доступные для редактирования в списке (прямо в таблице)
    # list_editable = ['status']

    # Группировка полей в форме редактирования
    date_hierarchy = "created_at"

    # Запрет удаления через админ-панель (опционально)
    # delete_allowed = False

    @admin.display(description="Действия")
    def action_buttons(self, obj):
        """
        Кнопки для быстрого изменения статуса заявки прямо в списке.
        (Только для pending-заявок).
        """
        if obj.status != "pending":
            return "Действия недоступны"

        buttons = ""
        for status, label in [("accepted", "Принять"), ("rejected", "Отклонить"), ("cancelled", "Отменить")]:
            url = f"/admin/skills/skillexchangerequest/{obj.id}/action/?status={status}"
            buttons += format_html('<a class="button" href="{}">{}</a> ', url, label)
        return format_html(buttons)

    action_buttons.allow_tags = True

    actions = ["mark_as_accepted", "mark_as_rejected", "mark_as_cancelled"]

    @admin.action(description="Принять выбранные заявки")
    def mark_as_accepted(self, request, queryset):
        queryset.update(status="accepted", responded_at=now())
        self.message_user(request, "Выбранные заявки приняты.")

    @admin.action(description="Отклонить выбранные заявки")
    def mark_as_rejected(self, request, queryset):
        queryset.update(status="rejected", responded_at=now())
        self.message_user(request, "Выбранные заявки отклонены.")

    @admin.action(description="Отменить выбранные заявки")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status="cancelled", responded_at=now())
        self.message_user(request, "Выбранные заявки отменены.")

    def get_urls(self):
        """URL для кастомных действий (кнопок в action_buttons)."""
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/action/",
                self.admin_site.admin_view(self.process_action),
                name="skillexchange_request_action",
            ),
        ]
        return custom_urls + urls

    def process_action(self, request, object_id):
        """Обрабатывает нажатие кнопок в action_buttons."""
        obj = get_object_or_404(SkillExchangeRequest, id=object_id)
        status = request.GET.get("status")

        if status in ["accepted", "rejected", "cancelled"]:
            obj.status = status
            obj.responded_at = now()
            obj.save()
            self.message_user(request, f"Заявка №{obj.id} {status}.")
        else:
            self.message_user(request, "Неверный статус.", level=messages.ERROR)
        return redirect("admin:skills_skillexchangerequest_changelist")


@admin.register(SkillLike)
class SkillLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "skill", "created_at"]
    search_fields = ["user__username", "skill__name"]
    raw_id_fields = ["user", "skill"]  # Для удобной выборки в админке
    date_hierarchy = "created_at"


@admin.register(SkillExchangeNotification)
class SkillExchangeNotificationAdmin(admin.ModelAdmin):
    """
    Админ-панель для уведомлений об обмене навыками.
    """

    list_display = [
        "id",
        "request__id",
        "recipient",
        "event_type",
        "is_read",
        "created_at",
    ]
    list_filter = [
        "event_type",
        "is_read",
    ]
    search_fields = [
        "recipient__username",
        "recipient__first_name",
        "recipient__last_name",
    ]

    # Поля, доступные для редактирования на странице списка
    date_hierarchy = "created_at"
    list_per_page = 20
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("request", "recipient")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Уведомления об обмене навыками"
        return super().changelist_view(request, extra_context)


@admin.register(WantsToLearn)
class WantsToLearnAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "subcategory", "created_at"]
    search_fields = ["user__username", "subcategory__name"]
