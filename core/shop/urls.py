from django.urls import path,re_path
from shop import views
from shop.feeds import LatestNewsFeed

app_name = 'shop'

urlpatterns = [
    path('add-or-remove-wishlist/', views.AddOrRemoveWishlistView.as_view(), name='add-or-remove-wishlist'),
    path("rss/feed/", LatestNewsFeed()),
    path('',views.ShopListProductView.as_view(),name='product-list'),
    re_path(r"(?P<slug>[-\w]+)/",views.ShopDetailProductView.as_view(),name='product-detail'),
    
]