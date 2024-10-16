# -*- coding: utf-8 -*-
"""Access token for blueking
"""
import datetime
import json
import logging

from django.utils.timezone import now
from django.utils.translation import get_language

from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.constants import ACCESS_PERMISSION_DENIED_CODE, ProviderType
from bkpaas_auth.core.exceptions import AccessPermissionDenied, InvalidTokenCredentialsError, ServiceError
from bkpaas_auth.core.http import http_get
from bkpaas_auth.core.services import get_app_credentials
from bkpaas_auth.core.user_info import BkUserInfo, RtxUserInfo, UserInfo
from bkpaas_auth.models import User
from bkpaas_auth.utils import scrub_data

logger = logging.getLogger(__name__)


class AbstractRequestBackend:
    def request_username(self, **credentials):
        """Get username through credentials"""


class TokenRequestBackend(AbstractRequestBackend):

    provider_type = ProviderType.BK

    def request_username(self, **credentials):
        """Get username through credentials"""
        is_success, resp = http_get(
            bkauth_settings.USER_COOKIE_VERIFY_URL,
            timeout=10,
            headers={
                'blueking-language': get_language(),
                "X-Bkapi-Authorization": json.dumps(dict(credentials, **get_app_credentials())),
            },
            params=credentials,
        )
        if not is_success:
            raise ServiceError('unable to fetch token services')
        if not isinstance(resp, dict):
            raise ValueError(f'response type expect dict, got: {resp}')

        # API 返回格式为：{"result": true, "code": 0, "message": "", "data": {"bk_username": "xxx"}}
        code = resp.get('code')
        if code == 0:
            return resp["data"]["bk_username"]

        logger.debug(
            f'Get user fail, url: {bkauth_settings.USER_COOKIE_VERIFY_URL}, '
            f'params: {scrub_data(credentials)}, response: {resp}'
        )

        # 用户认证成功，但用户无应用访问权限
        if code == ACCESS_PERMISSION_DENIED_CODE:
            raise AccessPermissionDenied(resp.get('message'))

        raise InvalidTokenCredentialsError('Invalid credentials given')


class RequestBackend(AbstractRequestBackend):

    provider_type = ProviderType.RTX

    def request_username(self, **credentials):
        """Get username through credentials"""
        is_success, resp = http_get(bkauth_settings.USER_COOKIE_VERIFY_URL, params=credentials, timeout=10)
        if not is_success:
            raise ServiceError('unable to fetch token services')
        if not isinstance(resp, dict):
            raise ValueError(f'response type expect dict, got: {resp}')

        # API 返回格式为：{"msg": "", "data": {"username": "xxx"}, "ret": 0}
        if resp.get('ret') != 0:
            logger.debug(
                f'Get user fail, url: {bkauth_settings.USER_COOKIE_VERIFY_URL}, '
                f'params: {scrub_data(credentials)}, response: {resp}'
            )
            raise InvalidTokenCredentialsError('Invalid credentials given')
        return resp["data"]["username"]


class LoginToken:
    """Access token object"""

    token_timeout_margin = 300

    def __init__(self, login_token=None, expires_in=None):
        assert login_token, 'Must provide token string'
        assert expires_in, 'Must provide expires_in seconds'
        self.login_token = login_token
        self.expires_at = now() + datetime.timedelta(seconds=expires_in)
        self.issued_at = now()
        self.user_info = UserInfo(username='AnonymousUser')

    def __str__(self):
        return 'token: {} expires_at: {}'.format(self.login_token, self.expires_at)

    def expired(self):
        return self.expires_at < now()

    def make_user(self, provider_type):
        self.user_info.provider_type = provider_type
        return create_user_from_token(self)


def mocked_create_user_from_token(
    token: LoginToken, provider_type: int = ProviderType.RTX, username: str = bkauth_settings.MOCKED_USER_NAME
) -> User:
    """Mocked create_user function, only for temporary use"""
    if provider_type == ProviderType.RTX:
        token.user_info = RtxUserInfo(
            LoginName=username,
            ChineseName=username,
        )
    elif provider_type == ProviderType.BK:
        token.user_info = BkUserInfo(bk_username=username, chname=username, email='', phone='')
    else:
        raise ValueError('Invalid provider_type given.')
    return create_user_from_token(token)


def create_user_from_token(token: LoginToken) -> User:
    """Create a user object from user info dict"""
    user = User(token=token)
    return token.user_info.provide(user)
