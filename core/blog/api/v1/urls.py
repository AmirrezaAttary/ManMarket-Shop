from django.urls import path,re_path
from blog.api.v1 import views

app_name = 'api-v1-blog'

urlpatterns = [
    path('post/',views.postList,name='api-v1-blog-posts'),
    path('post/<int:id>/',views.postDetail,name="api-v1-blog-post-detail")
]