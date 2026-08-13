# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.http import HttpRequest
from django.utils.timezone import now

from bkpaas_auth.conf import bkauth_settings

if TYPE_CHECKING:
    from bkpaas_auth.core.token import LoginToken

logger = logging.getLogger(__name__)


class BasePlugin:
    def get_credentials(self, request: HttpRequest) -> dict[str, str] | None:
        """获取登入态参数"""
        raise NotImplementedError

    def validate_login_token(self, login_token: LoginToken | None) -> bool:
        """校验 login_token 合法性"""
        if not login_token:
            return False

        if login_token.expired():
            return False
        return (now() - login_token.issued_at).total_seconds() <= bkauth_settings.SESSION_TIMEOUT


class BkTicketPlugin(BasePlugin):
    """Auth backend for bk_ticket"""

    def get_credentials(self, request: HttpRequest) -> dict[str, str] | None:
        bk_ticket = request.COOKIES.get("bk_ticket")

        if bk_ticket:
            return {
                "bk_ticket": bk_ticket,
            }

        return None


class BkTokenPlugin(BasePlugin):
    """Auth backend for bk_token"""

    def get_credentials(self, request: HttpRequest) -> dict[str, str] | None:
        bk_token = request.COOKIES.get("bk_token")

        if bk_token:
            return {"bk_token": bk_token}

        return None
