from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    SkillExchangeRequestViewSet,
    SkillImageViewSet,
    SkillLikeViewSet,
    SkillViewSet,
    SubCategoryViewSet,
    WantsToLearnViewSet,
)

router = DefaultRouter()
router.register(r"skills", SkillViewSet, basename="skill")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"subcategories", SubCategoryViewSet, basename="subcategory")
router.register(r"wants-to-learn", WantsToLearnViewSet, basename="wants-to-learn")
router.register(r"skill-images", SkillImageViewSet, basename="skill-image")
router.register(r"skill-exchange-requests", SkillExchangeRequestViewSet, basename="skill-exchange-request")
router.register(r"skill-likes", SkillLikeViewSet, basename="skill-like")


urlpatterns = [
    path("", include(router.urls)),
]
