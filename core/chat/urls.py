from django.urls import path
from chat import views

app_name = 'chat'

urlpatterns = [
    path('start/<int:product_id>/', views.StartChatView.as_view(), name='start_chat'),
    path('room/<int:pk>/', views.ChatRoomDetailView.as_view(), name='chat_room'),
    # path('room/', views.ChatRoomListView.as_view(), name='chat_room_list'),
]
