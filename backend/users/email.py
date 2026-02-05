import os

from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.email import PasswordResetEmail

User = get_user_model()


class CustomPasswordResetEmail(PasswordResetEmail):
    template_name = os.path.join(settings.BASE_DIR, "templates", "email", "password_reset.html")

    def get_context_data(self):
        context = super().get_context_data()
        context["site_name"] = settings.SITE_NAME
        context["domain"] = settings.DOMAIN
        context["site_email"] = settings.DEFAULT_FROM_EMAIL
        return context
