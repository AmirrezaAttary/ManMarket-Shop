from django.db import models
from django.contrib.auth import get_user_model
from ..accounts.models import UserType

User = get_user_model()
# Create your models here.
class ChatRoom(models.Model):
    product = models.ForeignKey("shop.ProductModel", on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_chats')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} | {self.customer.id} ↔ {self.admin.id}"
    
    def last_message(self):
        return self.chat_messages.order_by('-timestamp').first()
    
    def last_message_from_admin(self):
        last_msg = self.last_message()
        return last_msg and last_msg.sender.type in [UserType.admin.value, UserType.superuser.value]
    
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=['product', 'customer'], name='unique_product_customer_chat')
        ]


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.id}: {self.text[:30]}"