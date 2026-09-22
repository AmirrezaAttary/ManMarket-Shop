from django.urls import path, include
from rest_framework.routers import DefaultRouter


app_name = 'api-v1-reviews'


router = DefaultRouter()
router.register(r'review', views.ReviewViewsets, basename='review')

urlpatterns = router.urls