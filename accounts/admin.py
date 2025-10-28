from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import PasswordResetCode, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Roles & Status", {"fields": ("role", "is_banned")}),
    )
    list_display = (
        "username",
        "email",
        "role",
        "is_active",
        "is_banned",
    )
    list_filter = DjangoUserAdmin.list_filter + ("role", "is_banned")
    search_fields = DjangoUserAdmin.search_fields + ("role",)
    ordering = ("username",)


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "is_used", "expires_at", "created_at")
    list_filter = ("is_used", "expires_at")
    search_fields = ("user__username", "user__email", "code")
