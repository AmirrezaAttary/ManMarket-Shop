from django.urls import path,include
from .. import views

urlpatterns = [
    path("story/create/",views.AdminStoryCreateView.as_view(),name="story-create"),
    path("story/list/",views.AdminStoryListView.as_view(),name="story-list"),
    path("story/<int:pk>/edit/",views.AdminStoryEditView.as_view(),name="story-edit"),
    path("story/<int:pk>/delete/",views.AdminStoryDeleteView.as_view(),name="story-delete"),    
]
