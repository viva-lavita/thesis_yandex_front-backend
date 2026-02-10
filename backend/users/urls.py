from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CityViewSet, UserViewSet

app_name = "users"


router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("cities", CityViewSet, basename="cities")


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls.jwt")),
]
