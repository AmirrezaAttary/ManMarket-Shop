from django.urls import path,include

app_name = "admin"

urlpatterns = [
    path("",include("app.dashboard.admin.urls.generals")),
    path("",include("app.dashboard.admin.urls.profiles")),
    path("",include("app.dashboard.admin.urls.colors")),
    path("",include("app.dashboard.admin.urls.products")),
    path("",include("app.dashboard.admin.urls.products_color")),
    path("",include("app.dashboard.admin.urls.products_category")),
    path("",include("app.dashboard.admin.urls.products_brand")),
    path("",include("app.dashboard.admin.urls.product_specification")),
    path("",include("app.dashboard.admin.urls.coupons")),
    path("",include("app.dashboard.admin.urls.orders")),
    path("",include("app.dashboard.admin.urls.products_get_color")),
    path("",include("app.dashboard.admin.urls.blog")),
    path("",include("app.dashboard.admin.urls.db_media")),
    path("",include("app.dashboard.admin.urls.reviews")),
    path("",include("app.dashboard.admin.urls.blog_category")),
    path("",include("app.dashboard.admin.urls.contact")),
    path("",include("app.dashboard.admin.urls.chat")),
    path("",include("app.dashboard.admin.urls.story")),
    path("",include("app.dashboard.admin.urls.users")),
    path("",include("app.dashboard.admin.urls.person_pay")),
]