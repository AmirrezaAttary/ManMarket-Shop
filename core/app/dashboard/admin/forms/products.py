from django import forms
from ....shop.models import ProductModel, ProductImageModel,Color
from django_summernote.widgets import SummernoteWidget

class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = [
            "category",
            "title",
            "meta_title",
            "slug",
            "image",
            "description",
            "brief_description",
            "status",
            'brand',
            'warranty',
            'brief_title',
            'meta_description'
        ]
        widgets = {
            'description': SummernoteWidget(attrs={'summernote': {'height': '800px','width':'100%'}}),   # فقط روی این فیلد اعمال میشه
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['meta_title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-select'
        self.fields['brand'].widget.attrs['class'] = 'form-select'
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['brief_description'].widget.attrs['class'] = 'form-control'
        self.fields['brief_description'].widget.attrs['style'] = 'height: 200px'
        # self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['warranty'].widget.attrs['class'] = 'form-control'
        self.fields['brief_title'].widget.attrs['class'] = 'form-control'
        self.fields['meta_description'].widget.attrs['class'] = 'form-control'
        
        
class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImageModel
        fields = [
            "file",
            'color',
        ]
        
    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'form-control'
        self.fields['color'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['accept'] = 'image/png, image/webp, image/jpg, image/jpeg'

        if product:
            # استخراج رنگ‌هایی که از طریق موجودی رنگ تعریف شده‌اند
            colors = Color.objects.filter(product_inventories__product=product).distinct()
            if colors.exists():
                self.fields['color'].queryset = colors
            else:
                self.fields['color'].queryset = Color.objects.none()
                self.fields['color'].empty_label = 'بدون رنگ'
        else:
            self.fields['color'].queryset = Color.objects.none()
            self.fields['color'].empty_label = 'بدون رنگ'


class ProductImageColorForm(forms.ModelForm):
    class Meta:
        model = ProductImageModel
        fields = ['color']