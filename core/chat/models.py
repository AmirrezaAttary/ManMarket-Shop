from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.
class ChatRoom(models.Model):
    product = models.ForeignKey("shop.ProductModel", on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_chats')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} | {self.customer.email} ↔ {self.admin.email}"
    
    def last_message(self):
        return self.chat_messages.order_by('-timestamp').first()
    
    def last_message_from_admin(self):
        last_msg = self.last_message()
        return last_msg and last_msg.sender == self.admin
    class Meta:
        ordering = ["-created_at"]

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email}: {self.text[:30]}"