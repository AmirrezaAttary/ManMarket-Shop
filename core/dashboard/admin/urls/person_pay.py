from django.urls import path,include
from .. import views

urlpatterns = [
    path("person_pay/list/",views.AdminPersonPayListView.as_view(),name="person_pay-list"),
    # path("order/<int:pk>/detail/",views.AdminOrderDetailView.as_view(),name="order-detail"),
    # path("order/<int:pk>/edit/",views.AdminOrderEditView.as_view(),name="order-edit"),
    # path("order/<int:pk>/invoice/",views.AdminOrderInvoiceView.as_view(),name="order-invoice"),
]