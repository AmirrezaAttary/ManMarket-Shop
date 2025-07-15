from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("chat/list/",views.ChatRoomListView.as_view(),name="chat-list"),
    path("chat/detail/<int:pk>/",views.ChatRoomDetailView.as_view(),name="chat-detail"),

]