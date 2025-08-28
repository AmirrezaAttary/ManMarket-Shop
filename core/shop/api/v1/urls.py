from shop.api.v1 import views
from rest_framework.routers import DefaultRouter

app_name = 'api-v1-shop'

router = DefaultRouter()
router.register(r'product', views.ProductModelViewSet, basename='product')
router.register(r'category', views.ProductCategoryModelViewSet, basename='category')
router.register(r'brand', views.BrandModelViewSet, basename='brand')
router.register(r'color', views.ColorModelViewSet, basename='color')
router.register(r'inventory', views.ProductColorInventoryViewSet, basename='inventory')
router.register(r'images', views.ProductImageModelViewSet, basename='images')
router.register(r'specifications', views.ProductSpecificationViewSet, basename='specifications')

urlpatterns = router.urls
