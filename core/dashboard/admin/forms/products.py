from django import forms
from shop.models import ProductModel, ProductImageModel,ProductColorInventory, Color


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
            'brand',

        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['brand'].widget.attrs['class'] = 'form-control'
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



class ProductColorInventoryForm(forms.ModelForm):
    class Meta:
        model = ProductColorInventory
        fields = [
            'color',
            'stock',
            'discount_percent',
            'price',
        ] 

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        self.fields['color'].widget.attrs['class'] = 'form-control'
        self.fields['stock'].widget.attrs['class'] = 'form-control'
        self.fields['discount_percent'].widget.attrs['class'] = 'form-control'
        self.fields['price'].widget.attrs['class'] = 'form-control'


        if product:
            used_colors = ProductColorInventory.objects.filter(product=product).values_list('color_id', flat=True)
            self.fields['color'].queryset = Color.objects.exclude(id__in=used_colors)