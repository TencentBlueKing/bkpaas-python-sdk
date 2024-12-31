# -*- coding: utf-8 -*-
"""Access token for blueking
"""
import datetime
import json
import logging
from abc import abstractmethod
from typing import NamedTuple

from django.utils.timezone import now
from django.utils.translation import get_language

from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.constants import ACCESS_PERMISSION_DENIED_CODE, ProviderType
from bkpaas_auth.core.exceptions import (
    AccessPermissionDenied,
    HttpRequestError,
    InvalidTokenCredentialsError,
    ResponseError,
    ServiceError,
)
from bkpaas_auth.core.http import http_get, resp_to_json
from bkpaas_auth.core.services import get_app_credentials
from bkpaas_auth.core.user_info import BkUserInfo, RtxUserInfo, UserInfo
from bkpaas_auth.models import User
from bkpaas_auth.utils import scrub_data

logger = logging.getLogger(__name__)


class UserAccount(NamedTuple):
    """
    用户账号信息

    :param bk_username: 用户唯一标识，全局唯一
    :param display_name: 用户展示名.
    :param tenant_id: 用户所属租户 ID. 为 None 时表示用户无租户信息(可能接口不支持)
    """

    bk_username: str
    display_name: str
    tenant_id: str | None = None


class AbstractRequestBackend:
    def request_user_account(self, **credentials) -> UserAccount:
        """Get user account through credentials

        :raises ServiceError: When the backend service is not available.
        :raises ResponseError: When the backend response status code is not in the 20x range, nor 403.
        :raises AccessPermissionDenied: When the user does not have access permission.
        :raises InvalidTokenCredentialsError: When invalid credentials are provided.
        """
        if bkauth_settings.USER_INFO_APIGW_URL:
            return self._request_apigw(**credentials)

        return self._request_esb(**credentials)

    @staticmethod
    @abstractmethod
    def _request_apigw(**credentials):
        """get user account by apigw"""

    @staticmethod
    @abstractmethod
    def _request_esb(**credentials):
        """get user account by esb"""


class TokenRequestBackend(AbstractRequestBackend):

    provider_type = ProviderType.BK

    @staticmethod
    def _request_apigw(**credentials) -> UserAccount:
        try:
            resp = http_get(
                bkauth_settings.USER_INFO_APIGW_URL,
                timeout=10,
                headers={
                    'blueking-language': get_language(),
                    "X-Bkapi-Authorization": json.dumps(get_app_credentials()),
                    # 全租户应用，调用全租户网关时，网关会强制要求传递 X-Bk-Tenant-Id, 但不会实际校验值的有效性, 统一传 default
                    "X-Bk-Tenant-Id": "default",
                },
                params=credentials,
            )
        except HttpRequestError:
            raise ServiceError('Unable to request services')

        resp_json = resp_to_json(resp)

        if not isinstance(resp_json, dict):
            raise ValueError(f'response type expect dict, got: {resp_json}')

        if resp.status_code == 200:
            bk_username = resp_json["data"]["bk_username"]
            return UserAccount(
                bk_username=bk_username,
                display_name=resp_json["data"].get("display_name") or bk_username,
                tenant_id=resp_json["data"].get("tenant_id"),
            )

        if resp.status_code == 403:
            raise AccessPermissionDenied(resp_json["error"]["message"])

        raise ResponseError(resp_json["error"]["message"])

    @staticmethod
    def _request_esb(**credentials) -> UserAccount:
        try:
            resp = http_get(
                bkauth_settings.USER_COOKIE_VERIFY_URL,
                timeout=10,
                headers={
                    'blueking-language': get_language(),
                    "X-Bkapi-Authorization": json.dumps(dict(credentials, **get_app_credentials())),
                },
                params=credentials,
            )
        except HttpRequestError:
            raise ServiceError('unable to fetch token services')

        resp_json = resp_to_json(resp)

        if not isinstance(resp_json, dict):
            raise ValueError(f'response type expect dict, got: {resp_json}')

        # API 返回格式为：{"result": true, "code": 0, "message": "", "data": {"bk_username": "xxx"}}
        code = resp_json.get('code')
        if code == 0:
            username = resp_json["data"]["bk_username"]
            return UserAccount(bk_username=username, display_name=username)

        logger.debug(
            f'Get user fail, url: {bkauth_settings.USER_COOKIE_VERIFY_URL}, '
            f'params: {scrub_data(credentials)}, response: {resp_json}'
        )

        # 用户认证成功，但用户无应用访问权限
        if code == ACCESS_PERMISSION_DENIED_CODE:
            raise AccessPermissionDenied(resp_json.get('message'))

        raise InvalidTokenCredentialsError('Invalid credentials given')


class RequestBackend(AbstractRequestBackend):

    provider_type = ProviderType.RTX

    @staticmethod
    def _request_esb(**credentials) -> UserAccount:
        try:
            resp = http_get(bkauth_settings.USER_COOKIE_VERIFY_URL, params=credentials, timeout=10)
        except HttpRequestError:
            raise ServiceError('unable to fetch token services')

        resp_json = resp_to_json(resp)

        if not isinstance(resp_json, dict):
            raise ValueError(f'response type expect dict, got: {resp_json}')

        # API 返回格式为：{"msg": "", "data": {"username": "xxx"}, "ret": 0}
        if resp_json.get('ret') != 0:
            logger.debug(
                f'Get user fail, url: {bkauth_settings.USER_COOKIE_VERIFY_URL}, '
                f'params: {scrub_data(credentials)}, response: {resp_json}'
            )
            raise InvalidTokenCredentialsError('Invalid credentials given')

        username = resp_json["data"]["username"]
        return UserAccount(bk_username=username, display_name=username)

    @staticmethod
    def _request_apigw(**credentials):
        raise NotImplementedError("No APIGW for RTX Backend")


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
