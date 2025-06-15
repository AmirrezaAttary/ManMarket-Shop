from django import forms
from shop.models import ProductColorInventory, Color

class ProductColorInventoryForm(forms.ModelForm):
    class Meta:
        model = ProductColorInventory
        fields = [
            'color',
            'stock',
            'discount_percent',
            'price',
            'hex_color'
        ] 

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        self.fields['color'].widget.attrs['class'] = 'form-control'
        self.fields['stock'].widget.attrs['class'] = 'form-control'
        self.fields['discount_percent'].widget.attrs['class'] = 'form-control'
        self.fields['price'].widget.attrs['class'] = 'form-control'
        self.fields['hex_color'].widget.attrs['class'] = 'form-control'


        if product:
            used_colors = ProductColorInventory.objects.filter(product=product).values_list('color_id', flat=True)
            self.fields['color'].queryset = Color.objects.exclude(id__in=used_colors)