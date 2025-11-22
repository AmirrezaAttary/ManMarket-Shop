from django import forms
from ....pricegethamrh.models import PriceGetHamrh
from ....shop.models import ProductModel, ProductStatusType


class PriceGetHamrhForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        brand_slug = kwargs.pop('brand_slug', None)
        category_slug = kwargs.pop('category_slug', None)
        q = kwargs.pop('q', None)

        super().__init__(*args, **kwargs)

        # Bootstrap class
        for field in ['product', 'url', 'url_kasra', 'profit']:
            if field in self.fields:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': self.fields[field].label or ''
                })

        # Required settings
        self.fields['product'].required = True
        self.fields['product'].error_messages = {
            'required': 'لطفاً یک محصول انتخاب کنید.'
        }

        # url و url_kasra را به‌طور پیش‌فرض اختیاری می‌گذاریم
        self.fields['url'].required = False
        self.fields['url_kasra'].required = False

        # Custom queryset for new instances
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

            self.fields['product'].queryset = queryset.order_by('-id')
        else:
            self.fields['product'].queryset = ProductModel.objects.filter(
                id=self.instance.product_id,
                status=ProductStatusType.publish.value
            )

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        url_kasra = cleaned_data.get('url_kasra')

        if not url and not url_kasra:
            raise forms.ValidationError(
                "حداقل یکی از آدرس‌های محصول (HamrahTel یا KasraPars) باید وارد شود."
            )

        return cleaned_data

    class Meta:
        model = PriceGetHamrh
        fields = ['product', 'url', 'url_kasra', 'profit']
