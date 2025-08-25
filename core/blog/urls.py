from django.urls import path,re_path,include
from blog import views

app_name = 'blog'

urlpatterns = [
    path('api/v1/', include('blog.api.v1.urls')),
    path('',views.BlogListView.as_view(),name='blog-list'),
    re_path(r"(?P<slug>[-\w]+)/",views.BlogDetailView.as_view(),name='blog-detail'),
]