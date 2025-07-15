from django.urls import path,include

app_name = "admin"

urlpatterns = [
    path("",include("dashboard.admin.urls.generals")),
    path("",include("dashboard.admin.urls.profiles")),
    path("",include("dashboard.admin.urls.colors")),
    path("",include("dashboard.admin.urls.products")),
    path("",include("dashboard.admin.urls.products_color")),
    path("",include("dashboard.admin.urls.products_category")),
    path("",include("dashboard.admin.urls.products_brand")),
    path("",include("dashboard.admin.urls.product_specification")),
    path("",include("dashboard.admin.urls.coupons")),
    path("",include("dashboard.admin.urls.orders")),
    path("",include("dashboard.admin.urls.products_get_color")),
    path("",include("dashboard.admin.urls.blog")),
    path("",include("dashboard.admin.urls.db_media")),
    path("",include("dashboard.admin.urls.reviews")),
    path("",include("dashboard.admin.urls.blog_category")),
    path("",include("dashboard.admin.urls.contact")),
    path("",include("dashboard.admin.urls.chat")),
]