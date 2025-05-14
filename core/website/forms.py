from django import forms
from website.models import Contact


class ContatctForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ['message','email','name'] 
        
    