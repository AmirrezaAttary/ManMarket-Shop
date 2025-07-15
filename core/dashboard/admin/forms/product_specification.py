from django import forms
from getspecification.models import PriceSpecification
from shop.models import ProductModel,ProductSpecification


class SpecificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        brand_slug = kwargs.pop('brand_slug', None)  # ✅ درست
        print("brand_slug received in form:", brand_slug)  # ← بررسی مقدار
        super().__init__(*args, **kwargs)

        self.fields['product'].widget.attrs['class'] = 'form-control'
        self.fields['url'].widget.attrs['class'] = 'form-control'

        if not self.instance.pk:
            used_products = PriceSpecification.objects.values_list('product_id', flat=True)
            queryset = ProductModel.objects.exclude(id__in=used_products)

            if brand_slug:
                queryset = queryset.filter(brand__slug=brand_slug)

            self.fields['product'].queryset = queryset
        else:
            self.fields['product'].queryset = ProductModel.objects.filter(id=self.instance.product_id)
    class Meta:
        model = PriceSpecification
        fields = ['product', 'url']

            
            
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

        