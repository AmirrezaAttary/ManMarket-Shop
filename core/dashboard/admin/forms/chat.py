# chat/forms.py
from django import forms
from chat.models import Message

class AdminReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'متن پیام ...'}),
        }
