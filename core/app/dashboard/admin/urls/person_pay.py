from django.urls import path,include
from .. import views

urlpatterns = [
    path("person_pay/list/",views.AdminPersonPayListView.as_view(),name="person_pay-list"),
    path("person_pay/add/",views.AdminPersonPayCreateView.as_view(),name="person_pay-add"),
    # path("order/<int:pk>/edit/",views.AdminOrderEditView.as_view(),name="order-edit"),
    # path("order/<int:pk>/invoice/",views.AdminOrderInvoiceView.as_view(),name="order-invoice"),
]