from django import forms
from ....getspecification.models import PriceSpecification
from ....shop.models import ProductModel,ProductSpecification


class SpecificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        brand_slug = kwargs.pop('brand_slug', None)
        q = kwargs.pop('q', None)
        category_slug = kwargs.pop('category_slug', None)
        print("brand_slug received in form:", brand_slug)
        print("q received in form:", q)

        super().__init__(*args, **kwargs)

        self.fields['product'].required = True
        self.fields['product'].error_messages = {'required': 'لطفاً یک محصول انتخاب کنید.'}
        self.fields['product'].widget.attrs['class'] = 'form-control'

        self.fields['url'].required = True
        self.fields['url'].error_messages = {'required': 'لینک محصول را وارد کنید.'}
        self.fields['url'].widget.attrs['class'] = 'form-control'

        if not self.instance.pk:
            used_products = PriceSpecification.objects.values_list('product_id', flat=True)
            queryset = ProductModel.objects.exclude(id__in=used_products)

            if brand_slug:
                queryset = queryset.filter(brand__slug=brand_slug)
            if q:
                queryset = queryset.filter(title__icontains=q) | queryset.filter(id__iexact=q)
            if category_slug:
                queryset = queryset.filter(category__slug=category_slug)

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

        