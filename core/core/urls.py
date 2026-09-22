"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from app.dashboard.views import ProjectEntryView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions



schema_view = get_schema_view(
    openapi.Info(
        title="ManMarket APi",
        default_version="v1",
        description="this is a simple ManMarket api",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="programmer.amirrezaattary@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # The project is now admin-panel only: root is the secure entry point.
    path('', ProjectEntryView.as_view(), name='project-entry'),
    path('admin/', admin.site.urls),

    path('accounts/', include('app.accounts.urls')),
    path("dashboard/", include('app.dashboard.urls')),

    path('summernote/', include('django_summernote.urls')),
    
    path('api-auth/', include('rest_framework.urls')),
    # path(
    #     "swagger<format>/",
    #     schema_view.without_ui(cache_timeout=0),
    #     name="schema-json",
    # ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

if settings.SHOW_DEBUGGER_TOOLBAR:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls')),]
