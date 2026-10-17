from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "category", "body", "status"]
        widgets = {"body": forms.Textarea(attrs={"rows": 12})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = "No category"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {"body": "Add a comment"}
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}
