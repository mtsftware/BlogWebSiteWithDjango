from django import forms
from blogs.models import Page, Tag, Blog
from ckeditor.widgets import CKEditorWidget

class PageForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}),
        error_messages={'required': 'Title is required'},
    )
    class Meta:
        model = Page
        fields = ['title', 'category', 'image', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'category': forms.SelectMultiple(attrs={'class': 'form-control mb-3', 'id': 'id_category'}),
            'image': forms.ClearableFileInput(attrs={'type': 'file', 'class': 'form-control mb-3'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-control mb-3'}),
        }

class TagForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}),
        error_messages={'required': 'Title is required'},
    )
    class Meta:
        model = Tag
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-3'}),
        }

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'subtitle', 'tags', 'content', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control mb-3', 'id': 'id_tag'}),
            'content': CKEditorWidget(attrs={'class': 'form-control mb-3'}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-control mb-3'}),
        },
        error_messages = {
            'title': {'required': 'Title is required'},
            'subtitle': {'required': 'Subtitle is required'},
            'content': {'required': 'Content is required'},
        }
