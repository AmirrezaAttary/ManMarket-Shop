from django import forms
from ....order.models import UserAddressModel

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
        self.fields['state'].widget.attrs['class'] = 'form-control-custom my-1 fs-14'
        self.fields['city'].widget.attrs['class'] = 'form-control-custom my-1 fs-14'
        self.fields['zip_code'].widget.attrs['class'] = 'form-control-custom my-1 fs-14'
        self.fields['address'].widget.attrs['class'] = 'ws-cs-input form-label-custom'
        self.fields['address'].widget.attrs['rows'] = '3'