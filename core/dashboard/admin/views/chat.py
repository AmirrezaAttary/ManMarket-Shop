from django.views.generic import ListView, DetailView
from chat.models import ChatRoom

class ChatRoomListView(ListView):
    model = ChatRoom
    queryset = ChatRoom.objects.all()
    template_name = 'dashboard/admin/chat/chat_room_list.html'
    
    
class ChatRoomDetailView(DetailView):
    model = ChatRoom
    template_name = 'dashboard/admin/chat/chat_room_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['messages'] = self.object.messages.all()
        return context

