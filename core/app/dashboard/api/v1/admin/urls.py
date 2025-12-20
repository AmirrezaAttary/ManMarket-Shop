from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'admin'

router = DefaultRouter()
# router.register(r'profile', views.AdminProfileViewSet, basename='profile')
# router.register(r'security', views.AdminSecurityViewSet, basename='security')
router.register(r'product', views.ProductViewSet, basename='product')
router.register(r'inventory', views.InventoryViewSet, basename='inventory')
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'brand', views.BrandViewSet, basename='brand')
router.register(r'specification', views.SpecificationViewSet, basename='specification')
router.register(r'images', views.ProductImageViewSet, basename='productimage')
router.register(r'color', views.ColorViewSet, basename='color')
router.register(r'post', views.PostViewSet, basename='post')
router.register(r'post_category', views.PostCategoryViewSet, basename='post_category')
router.register(r'story', views.StoryViewSet, basename='story')
router.register(r'order', views.OrderViewSet, basename='order')
router.register(r'review', views.ReviewViewSet, basename='review')


urlpatterns = [
    path('', include(router.urls)),
]
