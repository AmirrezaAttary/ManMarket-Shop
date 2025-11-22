from django import forms
from ....website.models import Story

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = [
            "title",
            "status",
            "video",
            "icon",
            'product',
            'title_product',
        ] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['video'].widget.attrs['class'] = 'form-control'
        self.fields['icon'].widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'
        self.fields['product'].widget.attrs['class'] = 'form-select'
        self.fields['title_product'].widget.attrs['class'] = 'form-control'