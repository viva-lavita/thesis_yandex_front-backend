from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from users.models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "is_staff", "is_active", "created_at", "updated_at")
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active")
    readonly_fields = ("created_at", "updated_at")
    show_facets = admin.ShowFacets.ALWAYS
    ordering = ("email",)
    filter_horizontal = ("user_permissions",)

    fieldsets = (
        (None, {"fields": ("email", "password", "post")}),
        ("Персональная информация", {"fields": ("first_name", "last_name")}),
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
