from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("blog/list/",views.AdminBlogListView.as_view(),name="blog-list"),
    path("blog/create/",views.AdminBlogCreateView.as_view(),name="blog-create"),
    path("blog/<int:pk>/edit/",views.AdminBlogEditView.as_view(),name="blog-edit"),
    path("blog/<int:pk>/delete/",views.AdminBlogDeleteView.as_view(),name="blog-delete"),
]