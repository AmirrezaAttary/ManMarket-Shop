from django import forms
from blog.models import Category


class BlogCategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name',
        ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'



            
