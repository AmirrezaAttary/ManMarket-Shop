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
            "name",
            "phone_number"
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].widget.attrs['class'] = 'form-control-custom my-1 fs-14'
        self.fields['city'].widget.attrs['class'] = 'form-control-custom my-1 fs-14'
        self.fields['zip_code'].widget.attrs['class'] = 'form-control-custom my-1 fs-14'
        self.fields['name'].widget.attrs['class'] = 'form-control-custom my-1 fs-14'
        self.fields['name'].widget.attrs['style'] = 'max-width: 99%'
        self.fields['phone_number'].widget.attrs['class'] = 'form-control-custom my-1 fs-14'
        self.fields['phone_number'].widget.attrs['style'] = 'max-width: 99%'
        self.fields['address'].widget.attrs['class'] = 'ws-cs-input form-label-custom'
        self.fields['address'].widget.attrs['rows'] = '3'