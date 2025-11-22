from django import forms
from ....shop.models import ProductCategoryModel


class ProductCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ProductCategoryModel
        fields = [
            'title',
            'slug',
            'image'
        ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['image'].widget.attrs['class'] = 'form-control'


            
