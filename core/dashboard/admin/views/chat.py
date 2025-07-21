from django.views.generic import ListView, DetailView,FormView
from django.shortcuts import get_object_or_404, redirect, render
from chat.models import ChatRoom, Message
from  dashboard.admin.forms import AdminReplyForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from accounts.models import UserType

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

        # اگر کاربر فعلی ادمین چت نیست، ولی نوعش admin است → تغییر ادمین
        if request.user != self.chat.admin:
            if request.user.type == UserType.admin or request.user.type == UserType.superuser:
                self.chat.admin = request.user
                self.chat.save()
            else:
                return HttpResponseForbidden("شما اجازه پاسخ به این چت را ندارید.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        Message.objects.create(
            chat_room=self.chat,
            sender=self.request.user,
            text=form.cleaned_data['text']
        )
        return redirect('dashboard:admin:chat_room_send', pk=self.chat.pk)

    def get_context_data(self, **kwargs):
        chats = ChatRoom.objects.all()
        context = super().get_context_data(**kwargs)
        context['chat'] = self.chat
        context['chats'] = chats
        context['messages'] = self.chat.chat_messages.order_by('timestamp')
        return context