from django import forms
from pricegethamrh.models import PriceGetHamrh
from shop.models import ProductModel, ProductStatusType


class PriceGetHamrhForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        brand_slug = kwargs.pop('brand_slug', None)
        category_slug = kwargs.pop('category_slug', None)
        q = kwargs.pop('q', None)

        super().__init__(*args, **kwargs)

        # تنظیم کلاس برای Bootstrap
        self.fields['product'].widget.attrs['class'] = 'form-control'
        self.fields['url'].widget.attrs['class'] = 'form-control'

        # تنظیم اجبار و پیام خطا برای فیلد product
        self.fields['product'].required = True
        self.fields['product'].error_messages = {
            'required': 'لطفاً یک محصول انتخاب کنید.'
        }

        # تنظیم اجبار و پیام خطا برای فیلد url
        self.fields['url'].required = True
        self.fields['url'].error_messages = {
            'required': 'لینک محصول را وارد کنید.'
        }

        if not self.instance.pk:
            used_products = PriceGetHamrh.objects.values_list('product_id', flat=True)
            queryset = ProductModel.objects.filter(
                status=ProductStatusType.publish.value
            ).exclude(id__in=used_products)

            if brand_slug:
                queryset = queryset.filter(brand__slug=brand_slug)
            if q:
                queryset = queryset.filter(title__icontains=q) | queryset.filter(id__iexact=q)
            if category_slug:
                queryset = queryset.filter(category__slug=category_slug)

            self.fields['product'].queryset = queryset
        else:
            self.fields['product'].queryset = ProductModel.objects.filter(
                id=self.instance.product_id,
                status=ProductStatusType.publish.value
            )

    class Meta:
        model = PriceGetHamrh
        fields = ['product', 'url']