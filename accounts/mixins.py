from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles: tuple[str, ...] = ()
    require_super_admin: bool = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if getattr(request.user, "is_banned", False):
            raise Http404("Account banned.")
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        user = self.request.user
        if self.require_super_admin and getattr(user, "is_super_admin", False):
            return True
        if getattr(user, "is_super_admin", False):
            return True
        if not self.allowed_roles:
            return True
        return any(
            getattr(user, attr, False) for attr in self.allowed_roles
        )
