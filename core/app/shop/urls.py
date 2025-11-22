from django.urls import path,re_path,include
from . import views
from .feeds import LatestNewsFeed
from .api.v1 import urls

app_name = 'shop'

urlpatterns = [
    path('api/v1/', include(urls)),
    path('add-or-remove-wishlist/', views.AddOrRemoveWishlistView.as_view(), name='add-or-remove-wishlist'),
    path("rss/feed/", LatestNewsFeed()),
    path('',views.ShopListProductView.as_view(),name='product-list'),
    re_path(r"(?P<slug>[-\w]+)/",views.ShopDetailProductView.as_view(),name='product-detail'),
    
]