from django import forms
from blog.models import Post
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
            'content': SummernoteWidget(),  # فقط روی این فیلد اعمال میشه
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['slug'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'
        self.fields['tags'].widget.attrs['class'] = 'form-control'
        self.fields['image'].widget.attrs['class'] = 'form-control'
        # self.fields['content'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'