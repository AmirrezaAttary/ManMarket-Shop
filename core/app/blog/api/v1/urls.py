from app.blog.api.v1 import views
from rest_framework.routers import DefaultRouter

app_name = 'api-v1-blog'

router = DefaultRouter()
router.register(r'post', views.PostModelViewSet, basename='post')
router.register(r'category', views.CategoryModelViewSet, basename='category')

urlpatterns = router.urls
