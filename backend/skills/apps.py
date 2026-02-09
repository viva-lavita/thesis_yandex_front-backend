from django.apps import AppConfig

# from skills import signals  # noqa


class SkillsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "skills"
    verbose_name = "Навыки"

    def ready(self):
        import skills.signals  # noqa
