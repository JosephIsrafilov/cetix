from django import forms

from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("title", "category", "cover_image", "external_cover_url", "content")

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["cover_image"].required = False
        self.fields["cover_image"].widget.attrs.setdefault("accept", "image/*")
        self.fields["external_cover_url"].required = False
        self.fields["external_cover_url"].widget.attrs.update({"placeholder": "https://example.com/cover.jpg"})
        if user and getattr(user, "is_admin", False):
            self.fields["status"] = forms.ChoiceField(
                choices=[
                    choice
                    for choice in Article.STATUS_CHOICES
                    if choice[0] != Article.STATUS_REJECTED
                ],
                initial=self.instance.status if self.instance.pk else Article.STATUS_PUBLISHED,
            )
            status_field = self.fields.pop("status")
            self.fields["status"] = status_field

    def clean(self):
        cleaned = super().clean()
        cover_file = cleaned.get("cover_image")
        external_url = cleaned.get("external_cover_url")
        has_existing = False
        if self.instance and self.instance.pk:
            has_existing = bool(self.instance.cover_image or self.instance.external_cover_url)
        if not cover_file and not external_url and not has_existing:
            raise forms.ValidationError("Add a cover image or provide an external cover URL.")
        return cleaned

    def save(self, commit=True):
        article = super().save(commit=False)
        status = getattr(self, "cleaned_data", {}).get("status")
        if self.user and getattr(self.user, "is_admin", False) and status:
            article.status = status
        elif self.user and article.requires_moderation_for(self.user):
            article.status = Article.STATUS_PENDING
        external_url = self.cleaned_data.get("external_cover_url")
        if external_url:
            article.external_cover_url = external_url
        elif not self.cleaned_data.get("cover_image"):
            article.external_cover_url = ""
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
                "placeholder": "Share your thoughts...",
                "class": "comment-textarea",
            }
        ),
    )
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
