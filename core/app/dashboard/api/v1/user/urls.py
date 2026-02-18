from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'customer'

router = DefaultRouter()
# router.register(r'profile', views.UserProfileViewSet, basename='profile')
# router.register(r'security', views.UserSecurityViewSet, basename='security')
router.register(r'order', views.OrderViewSet, basename='order')
router.register(r'address', views.UserAddressModelViewSet, basename='address')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')
router.register(r"wallet", views.WalletViewSet, basename="wallet")
router.register(r"wallet/transactions", views.WalletTransactionViewSet, basename="wallet-transactions")



urlpatterns = [
    path('', include(router.urls)),
]
