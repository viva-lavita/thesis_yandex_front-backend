from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import health_check

app_name = "api"


router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("", include("users.urls")),
    path("utils/health-check/", health_check, name="health-check"),
]
