from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api-v1-website"

router = DefaultRouter()
router.register(r"banners", views.BannerViewSet, basename="banner")
router.register(r"faq", views.FAQViewSet, basename="faq")

urlpatterns = [
    path("site-setting/", views.SiteSettingAPIView.as_view(), name="site-setting"),
] + router.urls
