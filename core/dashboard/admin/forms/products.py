from django import forms
from shop.models import ProductModel, ProductImageModel


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = [
            "category",
            "title",
            "slug",
            "image",
            "description",
            "brief_description",
            "status",

        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['brief_description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        
        
class ProductImageForm(forms.ModelForm):


    class Meta:
        model = ProductImageModel
        fields = [
            "file",
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['accept'] = 'image/png, image/jpg, image/jpeg'