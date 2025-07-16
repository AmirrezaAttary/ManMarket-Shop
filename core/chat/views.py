from django.views import View
from django.views.generic import ListView
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from shop.models import ProductModel  # فرض بر اینکه این اسم مدل محصول شماست

from accounts.models import User, UserType  # مدل سفارشی شما

class StartChatView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        # فقط مشتری‌ها اجازه دارند چت بسازند
        if request.user.type != UserType.customer:
            return HttpResponseForbidden("دسترسی فقط برای مشتری‌ها مجاز است.")

        product = get_object_or_404(ProductModel, id=product_id)
        customer = request.user

        # پیدا کردن اولین ادمین موجود
        admin = User.objects.filter(type=UserType.admin).first()

        if not admin:
            return render(request, 'chat/no_admin.html', {'product': product})

        # جلوگیری از ساخت چت تکراری بین همین مشتری، محصول و ادمین
        chat, created = ChatRoom.objects.get_or_create(
            product=product,
            customer=customer,
            admin=admin
        )
        return redirect('chat:chat_room', pk=chat.pk)
    


class ChatRoomDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        chat = get_object_or_404(ChatRoom, pk=pk)

        if request.user != chat.customer and request.user != chat.admin:
            return render(request, 'chat/access_denied.html')

        messages = chat.chat_messages.order_by('timestamp')

        all_user_chats = ChatRoom.objects.filter(customer=request.user)

        return render(request, 'chat/room.html', {
            'chat_room': chat,    # چت جاری
            'messages': messages,
            'chats': all_user_chats  # لیست همه چت‌های کاربر
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
    
