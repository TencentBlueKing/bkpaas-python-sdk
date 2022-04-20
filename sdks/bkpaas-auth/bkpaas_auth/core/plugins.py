# -*- coding: utf-8 -*-
import logging

from bkpaas_auth.conf import bkauth_settings
from django.utils.timezone import now

logger = logging.getLogger(__name__)


class BasePlugin:
    def get_credentials(self, request):
        """获取登入态参数"""
        raise NotImplementedError

    def validate_login_token(self, login_token):
        """校验 login_token 合法性"""
        if not login_token:
            return False

        if login_token.expired():
            return False

        if (now() - login_token.issued_at).total_seconds() > bkauth_settings.SESSION_TIMEOUT:
            return False

        return True


class BkTicketPlugin(BasePlugin):
    """Auth backend for bk_ticket"""

    def get_credentials(self, request):
        bk_ticket = request.COOKIES.get('bk_ticket')

        if bk_ticket:
            return {
                'bk_ticket': bk_ticket,
            }

        return None


class BkTokenPlugin(BasePlugin):
    """Auth backend for bk_token"""

    def get_credentials(self, request):
        bk_token = request.COOKIES.get('bk_token')

        if bk_token:
            return {'bk_token': bk_token}

        return None
