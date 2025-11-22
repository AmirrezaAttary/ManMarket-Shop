from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("blog/list/",views.AdminBlogListView.as_view(),name="blog-list"),
    path("blog/create/",views.AdminBlogCreateView.as_view(),name="blog-create"),
    path("blog/<int:pk>/edit/",views.AdminBlogEditView.as_view(),name="blog-edit"),
    path("blog/<int:pk>/delete/",views.AdminBlogDeleteView.as_view(),name="blog-delete"),
    path("admin/blog/add-product/<int:post_id>/", views.AdminBlogAddProduct.as_view(), name="admin_blog_add_product"),
    path("admin/blog/delete-product/<int:pk>/", views.AdminBlogDeleteProduct.as_view(), name="admin_blog_delete_product"),

]