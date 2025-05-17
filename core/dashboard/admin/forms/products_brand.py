from django import forms
from shop.models import Brand


class BrandModelForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = [
            'title',
            'slug',
        ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'

            
