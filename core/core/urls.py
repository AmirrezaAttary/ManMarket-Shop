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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import sitemaps_dict

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.website.urls')),
    path("accounts/", include('app.accounts.urls')),
    path("product/", include('app.shop.urls')),
    path("cart/", include('app.cart.urls')),
    path("blog/", include('app.blog.urls')),
    path("dashboard/", include('app.dashboard.urls')),
    path('order/', include('app.order.urls')),
    path('payment/', include('app.payment.urls')),
    path('review/', include('app.review.urls')),
    path('pricegethamrh/', include('app.pricegethamrh.urls')),
    path('getspecification/', include('app.getspecification.urls')),
    path('faq/', include('app.faq.urls')),
    path('wallets/', include('app.wallets.urls')),
    path('chat/', include('app.chat.urls')),
    path('summernote/', include('django_summernote.urls')),
    
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps_dict}, name='django.contrib.sitemaps.views.sitemap'),

    path('robots.txt', include('robots.urls')),
    path('api-auth/', include('rest_framework.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

if settings.SHOW_DEBUGGER_TOOLBAR:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls')),]
