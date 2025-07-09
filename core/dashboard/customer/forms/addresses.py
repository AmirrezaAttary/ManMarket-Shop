from django import forms
from order.models import UserAddressModel

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddressModel
        fields= [
            "address",
            "state",
            "city",
            "zip_code",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].widget.attrs['class'] = 'ws-cs-input'
        self.fields['city'].widget.attrs['class'] = 'ws-cs-input'
        self.fields['zip_code'].widget.attrs['class'] = 'ws-cs-input'
        self.fields['address'].widget.attrs['class'] = 'ws-cs-input'