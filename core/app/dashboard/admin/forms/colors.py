from django import forms
from ....shop.models import Color


class ColorModelForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = [
            'title',
        ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'


            
