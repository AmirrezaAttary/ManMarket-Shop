from django import forms
from pricegethamrh.models import PriceGetHamrh
from shop.models import ProductModel, ProductStatusType


class PriceGetHamrhForm(forms.ModelForm):
    class Meta:
        model = PriceGetHamrh
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
            used_products = PriceGetHamrh.objects.values_list('product_id', flat=True)
            self.fields['product'].queryset = ProductModel.objects.filter(
                status=ProductStatusType.publish.value
            ).exclude(id__in=used_products)
        else:
            self.fields['product'].queryset = ProductModel.objects.filter(
                id=self.instance.product_id,
                status=ProductStatusType.publish.value
            )

        