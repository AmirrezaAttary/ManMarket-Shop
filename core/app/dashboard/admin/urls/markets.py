from django.urls import path

from .. import views

urlpatterns = [
    path("markets/", views.AdminMarketsView.as_view(), name="markets"),
]
