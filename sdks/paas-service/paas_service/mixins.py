# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin as _LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from paas_service.constants import REDIRECT_FIELD_NAME


class LoginRequiredMixin(_LoginRequiredMixin):
    """
    CBV mixin which verifies that the current user is authenticated,
    Which use the absolute uri when redirecting to login.
    """

    redirect_field_name = REDIRECT_FIELD_NAME

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(
            self.request.build_absolute_uri(), self.get_login_url(), self.get_redirect_field_name()
        )
