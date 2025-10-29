from urllib.parse import quote_plus

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):

    ROLE_SUPER_ADMIN = "super_admin"
    ROLE_ADMIN = "admin"
    ROLE_USER = "user"

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, "Super Admin"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_USER, "User"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_USER,
    )
    is_banned = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
        if self.is_banned:
            self.is_active = False
        if self.is_superuser:
            self.role = self.ROLE_SUPER_ADMIN
            self.is_staff = True
        elif self.role == self.ROLE_SUPER_ADMIN:
            self.is_superuser = True
            self.is_staff = True
        elif self.role == self.ROLE_ADMIN:
            self.is_staff = True
            self.is_superuser = False
        else:
            self.is_staff = False
            self.is_superuser = False
        if update_fields is not None:
            update_fields.update({"is_staff", "is_superuser"})
            if self.is_banned:
                update_fields.add("is_active")
            kwargs["update_fields"] = list(update_fields)
        super().save(*args, **kwargs)

    @property
    def is_super_admin(self) -> bool:
        return self.role == self.ROLE_SUPER_ADMIN or self.is_superuser

    @property
    def is_admin(self) -> bool:
        return self.role in {self.ROLE_SUPER_ADMIN, self.ROLE_ADMIN} or self.is_staff

    def ban(self):
        self.is_banned = True
        self.is_active = False
        self.save(update_fields=["is_banned", "is_active"])

    def unban(self):
        self.is_banned = False
        self.is_active = True
        self.save(update_fields=["is_banned", "is_active"])

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        seed = (self.first_name or self.username or "User").strip() or "User"
        return (
            "https://ui-avatars.com/api/?background=1d2533&color=ffffff&name="
            f"{quote_plus(seed[:24])}"
        )


class PasswordResetCode(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_codes"
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Reset code for {self.user} ({self.code})"

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    def is_valid(self) -> bool:
        return (
            not self.is_used
            and self.expires_at >= timezone.now()
        )
