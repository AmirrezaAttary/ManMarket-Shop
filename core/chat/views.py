from django.views import View
from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from shop.models import ProductModel  # فرض بر اینکه این اسم مدل محصول شماست

from accounts.models import User, UserType  # مدل سفارشی شما

class StartChatView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(ProductModel, id=product_id)
        customer = request.user

        # فیلتر فقط ادمین‌ها بر اساس نوع
        admin = User.objects.filter(type=UserType.admin).first()

        if not admin:
            return render(request, 'chat/no_admin.html', {'product': product})

        # جلوگیری از ساخت چت تکراری
        chat, created = ChatRoom.objects.get_or_create(
            product=product,
            customer=customer,
            admin=admin
        )
        return redirect('chat:chat_room', pk=chat.pk)
    


class ChatRoomDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        chat = get_object_or_404(ChatRoom, pk=pk)

        # بررسی اینکه فقط خود مشتری یا ادمین مرتبط می‌تونه چت رو ببینه
        if request.user != chat.customer and request.user != chat.admin:
            return render(request, 'chat/access_denied.html')

        messages = chat.chat_messages.order_by('timestamp')
        chat_room = ChatRoom.objects.filter(customer=request.user)
        return render(request, 'chat/room.html', {
            'chat': chat,
            'messages': messages,
            'chat_room': chat_room
        })

    def post(self, request, pk):
        chat = get_object_or_404(ChatRoom, pk=pk)

        if request.user != chat.customer and request.user != chat.admin:
            return render(request, 'chat/access_denied.html')

        text = request.POST.get('message')
        if text:
            Message.objects.create(
                chat_room=chat,
                sender=request.user,
                text=text
            )
        return redirect('chat:chat_room', pk=chat.pk)
    
    
class ChatRoomListView(LoginRequiredMixin, ListView):
    template_name = 'chat/room_list.html'
    
    def get_queryset(self):
        queryset =  ChatRoom.objects.filter(customer=self.request.user)
        return queryset
    
