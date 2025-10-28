import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, FormView, ListView, TemplateView

from .forms import (
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    ProfileForm,
    SignUpForm,
)
from .mixins import RoleRequiredMixin
from .models import PasswordResetCode, User


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("articles:article_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Welcome aboard! Your account is ready.")
        return response


class UserListView(RoleRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    allowed_roles = ("is_admin",)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(role=User.ROLE_SUPER_ADMIN)
            .order_by("username")
        )


class UserBanToggleView(RoleRequiredMixin, View):
    allowed_roles = ("is_admin",)

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target.role == User.ROLE_SUPER_ADMIN or target == request.user:
            raise Http404("Cannot change status for this user.")
        if target.role == User.ROLE_ADMIN and not request.user.is_super_admin:
            raise Http404("Only super admins can ban other admins.")

        if target.is_banned:
            target.unban()
            messages.success(request, f"{target.username} was unbanned.")
        else:
            target.ban()
            messages.success(request, f"{target.username} was banned.")
        return HttpResponseRedirect(reverse("accounts:user_list"))


class UserRoleUpdateView(RoleRequiredMixin, View):
    require_super_admin = True

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target == request.user or target.role == User.ROLE_SUPER_ADMIN:
            raise Http404("Cannot modify this user.")

        action = request.POST.get("action")
        if action == "promote":
            target.role = User.ROLE_ADMIN
            target.is_banned = False
            target.is_active = True
            target.save(update_fields=["role", "is_banned", "is_active"])
            messages.success(request, f"{target.username} promoted to admin.")
        elif action == "demote":
            target.role = User.ROLE_USER
            target.save(update_fields=["role"])
            messages.success(request, f"{target.username} demoted to user.")
        else:
            raise Http404("Unknown action.")
        return HttpResponseRedirect(reverse("accounts:user_list"))


class PasswordResetRequestView(FormView):
    template_name = "accounts/password_reset_request.html"
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy("accounts:password_reset_done")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            pass
        else:
            if not user.is_banned:
                PasswordResetCode.objects.filter(
                    user=user, is_used=False
                ).update(is_used=True)
                code = f"{secrets.randbelow(10**6):06d}"
                expires_at = timezone.now() + timedelta(minutes=15)
                PasswordResetCode.objects.create(
                    user=user,
                    code=code,
                    expires_at=expires_at,
                )
                send_mail(
                    subject="Your Cetix password reset code",
                    message=(
                        "We received a request to reset your Cetix password.\n\n"
                        f"Your verification code is: {code}\n"
                        "This code will expire in 15 minutes.\n\n"
                        "If you did not request this, you can ignore this email."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
        messages.success(
            self.request,
            "If an account with that email exists, we've sent a verification code.",
        )
        return super().form_valid(form)


class PasswordResetRequestedView(TemplateView):
    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirmView(FormView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        code = form.cleaned_data["code"]
        new_password = form.cleaned_data["new_password1"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            form.add_error(None, "Invalid email or verification code.")
            return self.form_invalid(form)

        reset_code = (
            PasswordResetCode.objects.filter(
                user=user,
                code=code,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )
        if not reset_code or not reset_code.is_valid():
            form.add_error("code", "Invalid or expired verification code.")
            return self.form_invalid(form)

        user.set_password(new_password)
        user.save()
        reset_code.mark_used()
        messages.success(
            self.request,
            "Password updated. You can now log in with your new credentials.",
        )
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return HttpResponseRedirect(request.path)
        return render(request, self.template_name, {"form": form})
