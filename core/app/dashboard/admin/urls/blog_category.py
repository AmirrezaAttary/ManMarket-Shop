from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("blog/category/list/",views.AdminBlogCategoryListView.as_view(),name="blog-category-list"),
    path("blog/category/add/",views.AdminBlogCategoryCreateView.as_view(),name="blog-category-add"),
    path("blog/category/<int:pk>/delete/",views.AdminBlogCategoryDeleteView.as_view(),name="blog-category-delete"),
    path("blog/category/<int:pk>/edi/",views.AdminBlogCategoryEditView.as_view(),name="blog-category-edit"),
]