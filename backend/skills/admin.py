from django.contrib import admin

from skills.models import Category, Skill, SkillImage, SubCategory


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
