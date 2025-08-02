from django import forms
from blog.models import Post,PostProduct
from django_summernote.widgets import SummernoteWidget
from shop.models import ProductModel, ProductStatusType

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'image' ,
            'title' ,
            'content' ,
            'category' ,
            'status' ,
            'slug' ,
            'tags',
            'meta_description'
        ]
        widgets = {
            'content': SummernoteWidget(attrs={'summernote': {'height': '800px','width':'100%'}}),  # فقط روی این فیلد اعمال میشه
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['style'] = 'height: 100px'
        self.fields['tags'].widget.attrs['class'] = 'form-control'
        self.fields['image'].widget.attrs['class'] = 'form-control'
        self.fields['meta_description'].widget.attrs['class'] = 'form-control'
        # self.fields['content'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        
        
class BlogPostProductForm(forms.ModelForm):
    class Meta:
        model = PostProduct
        fields = ['product']

    def __init__(self, *args, **kwargs):
        brand_slug = kwargs.pop('brand_slug', None)
        category_slug = kwargs.pop('category_slug', None)
        q = kwargs.pop('q', None)

        super().__init__(*args, **kwargs)

        self.fields['product'].widget.attrs['class'] = 'form-select'
        self.fields['product'].required = True
        self.fields['product'].error_messages = {
            'required': 'لطفاً یک محصول انتخاب کنید.'
        }

        used_product_ids = PostProduct.objects.values_list('product_id', flat=True)

        if not self.instance.pk:
            queryset = ProductModel.objects.filter(
                status=ProductStatusType.publish.value
            ).exclude(id__in=used_product_ids)

            if brand_slug:
                queryset = queryset.filter(brand__slug=brand_slug)

            if category_slug:
                queryset = queryset.filter(category__slug=category_slug)

            if q:
                queryset = queryset.filter(title__icontains=q) | queryset.filter(id__iexact=q)

            self.fields['product'].queryset = queryset.distinct()
        else:
            # برای حالت ویرایش: فقط همان محصول انتخاب‌شده را نشان بده
            self.fields['product'].queryset = ProductModel.objects.filter(
                id=self.instance.product_id,
                status=ProductStatusType.publish.value
            )