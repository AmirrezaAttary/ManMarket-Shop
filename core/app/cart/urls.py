from django.urls import path,include
from . import views
from .api.v1 import urls

app_name = "cart"

urlpatterns = [
    path('v1/', include(urls)),
    path('session/add-product/',views.SessionAddProduct.as_view(),name='session-add-product'),
    path('summary/',views.SessionCartSummry.as_view(),name='cart-summery'),
    path("session/update-product-quantity/",views.SessionUpdateProductQuantityView.as_view(),name="session-update-product-quantity"),
    path("session/remove-product/",views.SessionRemoveProductView.as_view(),name="session-remove-product"),
    path('session/remove/one/quantity/',views.SessionCartProductRemoveOneQuantityView.as_view(),name='session-remove-one-quantity'),
    path('session/remove/add/quantity/',views.SessionCartProductAddOneQuantityView.as_view(),name='session-add-one-quantity'),

]

