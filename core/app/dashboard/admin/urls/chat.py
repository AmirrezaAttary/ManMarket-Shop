from django.urls import path, include
from .. import views
 
 
urlpatterns = [
    path("chat/list/",views.ChatRoomListView.as_view(),name="chat-list"),
    path("chat/detail/<int:pk>/",views.ChatRoomDetailView.as_view(),name="chat-detail"),
    path('chat/<int:pk>/reply/', views.ChatRoomSendView.as_view(), name='chat_room_send'),

]