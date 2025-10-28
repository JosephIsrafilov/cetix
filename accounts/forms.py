from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = User.ROLE_USER
        if commit:
            user.save()
        return user


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("role",)

    def clean_role(self):
        role = self.cleaned_data["role"]
        if role == User.ROLE_SUPER_ADMIN:
            raise forms.ValidationError("Only existing super admins can create other super admins.")
        return role


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class PasswordResetConfirmForm(forms.Form):
    email = forms.EmailField()
    code = forms.CharField(max_length=6, min_length=6)
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("new_password1")
        password2 = cleaned.get("new_password2")
        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "Passwords do not match.")
        return cleaned

    def clean_code(self):
        code = self.cleaned_data["code"]
        if not code.isdigit():
            raise forms.ValidationError("Verification code must contain only digits.")
        return code
