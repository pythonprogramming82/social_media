from django import forms
from .models import Post, Comment

class PostCreatUpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("body",)


class CreatFormComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)


class CommentReolyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)


class SearchForm(forms.Form):
    search = forms.CharField()