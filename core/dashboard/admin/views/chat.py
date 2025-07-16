from django.views.generic import ListView, DetailView,FormView
from django.shortcuts import get_object_or_404, redirect, render
from chat.models import ChatRoom, Message
from  dashboard.admin.forms import AdminReplyForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

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


class ChatRoomSendView(LoginRequiredMixin, FormView):
    template_name = 'dashboard/admin/chat/chat_room_send.html'
    form_class = AdminReplyForm

    def dispatch(self, request, *args, **kwargs):
        self.chat = get_object_or_404(ChatRoom, pk=kwargs['pk'])

        # بررسی اینکه کاربر ادمین چت هست یا نه
        if request.user != self.chat.admin:
            return HttpResponseForbidden("فقط ادمین مربوطه می‌تواند پاسخ دهد.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # ساخت پیام جدید توسط ادمین
        Message.objects.create(
            chat_room=self.chat,
            sender=self.request.user,
            text=form.cleaned_data['text']
        )
        return redirect('dashboard:admin:chat_room_send', pk=self.chat.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat'] = self.chat
        context['messages'] = self.chat.chat_messages.order_by('timestamp')
        return context