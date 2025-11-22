from ...api.v1 import views
from rest_framework.routers import DefaultRouter

app_name = 'api-v1-shop'

router = DefaultRouter()
router.register(r'product', views.ProductModelViewSet, basename='product')
router.register(r'category', views.ProductCategoryModelViewSet, basename='category')
router.register(r'brand', views.BrandModelViewSet, basename='brand')
router.register(r'color', views.ColorModelViewSet, basename='color')

urlpatterns = router.urls
