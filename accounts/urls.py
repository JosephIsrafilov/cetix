from django.urls import path

from .views import (
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PasswordResetRequestedView,
    SignUpView,
    UserBanToggleView,
    UserListView,
    UserRoleUpdateView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", SignUpView.as_view(), name="register"),
    path("password/forgot/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/forgot/done/", PasswordResetRequestedView.as_view(), name="password_reset_done"),
    path("password/verify/", PasswordResetConfirmView.as_view(), name="password_reset_verify"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/ban/", UserBanToggleView.as_view(), name="user_ban_toggle"),
    path(
        "users/<int:pk>/role/",
        UserRoleUpdateView.as_view(),
        name="user_role_update",
    ),
]
