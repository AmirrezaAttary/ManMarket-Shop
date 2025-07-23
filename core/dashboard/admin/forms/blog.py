from django import forms
from blog.models import Post,PostProduct
from django_summernote.widgets import SummernoteWidget

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
            'tags'
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
        # self.fields['content'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        
        
class BlogPostProductForm(forms.ModelForm):
    class Meta:
        model = PostProduct
        fields = [
            'post',
            'product',
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].widget.attrs['class'] = 'form-select'