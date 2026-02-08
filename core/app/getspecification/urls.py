from django.urls import path,re_path
from . import views

app_name = "getspecification"

urlpatterns = [
    # path("specification/<int:pk>/",views.GetSpecification.as_view(),name="specification"),
    # path('get-all-specifications/', views.GetAllSpecifications.as_view(), name='get-all-specifications'),
    path('get-comments/<int:pk>/', views.GetComment.as_view(), name='get-comments'),
]