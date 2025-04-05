from django.urls import path,re_path
from shop import views

app_name = 'shop'

urlpatterns = [
    path('',views.ShopListProductView.as_view(),name='product-list'),
    re_path(r"(?P<slug>[-\w]+)/",views.ShopDetailProductView.as_view(),name='product-detail'),
]