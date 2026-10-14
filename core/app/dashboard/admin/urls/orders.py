from django.urls import path,include
from .. import views

urlpatterns = [
    path("order/list/",views.AdminOrderListView.as_view(),name="order-list"),
    path("order/<int:pk>/detail/",views.AdminOrderDetailView.as_view(),name="order-detail"),
    path("order/<int:pk>/edit/",views.AdminOrderEditView.as_view(),name="order-edit"),
    path("order/<int:pk>/invoice/",views.AdminOrderInvoiceView.as_view(),name="order-invoice"),
    path("order/<int:pk>/bwdk/verify/",views.AdminOrderBWDKVerifyView.as_view(),name="order-bwdk-verify"),
    path("order/<int:pk>/bwdk/refund/",views.AdminOrderBWDKRefundView.as_view(),name="order-bwdk-refund"),
]