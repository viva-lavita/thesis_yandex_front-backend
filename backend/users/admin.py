from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from users.models import City, User

admin.site.unregister(Group)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("id", "name")


# Сделать поля обязательными, чтобы у фронтов валидировалось
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "is_staff", "created_at", "updated_at")
    search_fields = ("email", "name", "city__name", "email")
    list_filter = ("is_staff", "gender")
    readonly_fields = ("created_at", "updated_at")
    show_facets = admin.ShowFacets.ALWAYS
    ordering = ("-created_at",)
    filter_horizontal = ("user_permissions",)
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("name", "city", "date_of_birth", "gender", "about", "avatar")}),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (("Важные даты"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "usable_password", "password1", "password2"),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Делаем поля обязательными в админ-форме
        for field_name in ["name", "city", "date_of_birth", "gender"]:
            if field_name in form.base_fields:
                form.base_fields[field_name].required = True
        return form
