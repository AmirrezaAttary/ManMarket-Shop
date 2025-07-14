from django import forms
from getspecification.models import PriceSpecification
from shop.models import ProductModel,ProductSpecification


class SpecificationForm(forms.ModelForm):
    class Meta:
        model = PriceSpecification
        fields = [
            'product',
            'url',
        ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # افزودن کلاس CSS برای Bootstrap
        self.fields['product'].widget.attrs['class'] = 'form-control'
        self.fields['url'].widget.attrs['class'] = 'form-control'

        if not self.instance.pk:
            # فقط محصولاتی که هنوز PriceSpecification ندارند
            used_products = PriceSpecification.objects.values_list('product_id', flat=True)
            self.fields['product'].queryset = ProductModel.objects.exclude(id__in=used_products)
        else:
            # در حالت ویرایش، فقط همان محصول مربوط به این نمونه
            self.fields['product'].queryset = ProductModel.objects.filter(id=self.instance.product_id)
            
            
class SpecificationCreateForm(forms.ModelForm):
    class Meta:
        model = ProductSpecification
        fields = [
            'name',
            'value',
            'status',
        ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # افزودن کلاس CSS برای Bootstrap
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['value'].widget.attrs['class'] = 'form-control'
        # self.fields['status'].widget.attrs['class'] = 'form-control'

        