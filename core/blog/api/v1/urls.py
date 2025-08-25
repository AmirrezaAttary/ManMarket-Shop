from django.urls import path,re_path
from blog.api.v1 import views

app_name = 'api-v1-blog'

urlpatterns = [
    path('posts/',views.postList,name='api-v1-blog-posts'),
]