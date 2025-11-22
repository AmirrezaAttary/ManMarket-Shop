from django.urls import path,include

app_name = "customer"

urlpatterns = [
    path("",include("app.dashboard.customer.urls.generals")),
    path("",include("app.dashboard.customer.urls.profiles")),
    path("",include("app.dashboard.customer.urls.addresses")),
    path("",include("app.dashboard.customer.urls.orders")),
    path("",include("app.dashboard.customer.urls.wishlists")),
    path("",include("app.dashboard.customer.urls.wallets")),
]