from django.urls import path

from .. import views
from ..crud import BANNER, FAQ_CONFIG, QUESTION
from ..views.crud import build_crud_views


def crud_paths(config, views_map):
    key = config.key
    paths = [
        path(f"{key}/list/", views_map["list"].as_view(), name=f"{key}-list"),
        path(f"{key}/<int:pk>/edit/", views_map["edit"].as_view(), name=f"{key}-edit"),
        path(f"{key}/<int:pk>/delete/", views_map["delete"].as_view(), name=f"{key}-delete"),
    ]
    if config.can_add:
        paths.append(path(f"{key}/add/", views_map["add"].as_view(), name=f"{key}-add"))
    return paths


urlpatterns = [
    # مگا منو (فرم افزودن چندبرندی دارد)
    path("mega-menu/list/", views.AdminMegaMenuListView.as_view(), name="mega-menu-list"),
    path("mega-menu/add/", views.AdminMegaMenuCreateView.as_view(), name="mega-menu-add"),
    path("mega-menu/<int:pk>/edit/", views.AdminMegaMenuUpdateView.as_view(), name="mega-menu-edit"),
    path("mega-menu/<int:pk>/delete/", views.AdminMegaMenuDeleteView.as_view(), name="mega-menu-delete"),

    # تنظیمات سایت (تک‌رکوردی)
    path("site-setting/", views.AdminSiteSettingView.as_view(), name="site-setting"),
]

for _config in (BANNER, FAQ_CONFIG, QUESTION):
    urlpatterns += crud_paths(_config, build_crud_views(_config))
