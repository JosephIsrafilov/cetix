from django import forms

from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("title", "category", "cover_image", "content")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user and getattr(user, "is_admin", False):
            self.fields["status"] = forms.ChoiceField(
                choices=[
                    choice
                    for choice in Article.STATUS_CHOICES
                    if choice[0] != Article.STATUS_REJECTED
                ],
                initial=self.instance.status if self.instance.pk else Article.STATUS_PUBLISHED,
            )
            self.fields.move_to_end("status")

    def save(self, commit=True):
        article = super().save(commit=False)
        status = getattr(self, "cleaned_data", {}).get("status")
        if self.user and getattr(self.user, "is_admin", False) and status:
            article.status = status
        elif self.user and article.requires_moderation_for(self.user):
            article.status = Article.STATUS_PENDING
        if commit:
            article.save()
            self.save_m2m()
        return article


class ArticleModerationForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("status",)

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status not in {
            Article.STATUS_PUBLISHED,
            Article.STATUS_REJECTED,
        }:
            raise forms.ValidationError("Choose publish or reject.")
        return status


class CommentForm(forms.Form):
    body = forms.CharField(
        label="Add a comment",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Share your thoughts…",
                "class": "comment-textarea",
            }
        ),
    )
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
