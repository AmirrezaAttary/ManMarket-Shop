from django.urls import path,re_path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('',views.BlogListView.as_view(),name='blog-list'),
    re_path(r"(?P<slug>[-\w]+)/",views.BlogDetailView.as_view(),name='blog-detail'),

]