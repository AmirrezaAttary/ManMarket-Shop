from django.urls import path,re_path,include
from . import views
from .api.v1 import urls as api_v1_urls

app_name = 'blog'

urlpatterns = [
    path('api/v1/', include(api_v1_urls)),
    path('',views.BlogListView.as_view(),name='blog-list'),
    re_path(r"(?P<slug>[-\w]+)/",views.BlogDetailView.as_view(),name='blog-detail'),
]