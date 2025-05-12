from django import forms
from shop.models import Brand, ProductCategoryModel


class ProductCategoryModelForm(forms.ModelForm):
    class Meta:
        model = ProductCategoryModel
        fields = [
            'title',
            'slug',
        ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'


            
