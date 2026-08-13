# -*- coding: utf-8 -*-
"""Access token for blueking"""

from __future__ import annotations

import datetime
import json
import logging
from abc import abstractmethod
from typing import Any, ClassVar, NamedTuple

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
from bkpaas_auth.core.http import async_http_get, http_get, resp_to_json
from bkpaas_auth.core.services import get_app_credentials
from bkpaas_auth.core.user_info import BkUserInfo, RtxUserInfo, UserInfo
from bkpaas_auth.models import User
from bkpaas_auth.utils import deserialize_datetime, scrub_data, serialize_datetime

logger = logging.getLogger(__name__)

# Constants related with serialization of UserInfo in LoginToken.
#
# The field name to store the type of user_info instance.
_USER_INFO_TYPE_FIELD = "_user_info_type"
# The mapping between user_info type name and the actual class.
_USER_INFO_TYPES: dict[str, type[UserInfo]] = {
    UserInfo.__name__: UserInfo,
    RtxUserInfo.__name__: RtxUserInfo,
    BkUserInfo.__name__: BkUserInfo,
}


class UserAccount(NamedTuple):
    """
    用户账号信息

    :param bk_username: 用户唯一标识，全局唯一
    :param display_name: 用户展示名.
    :param time_zone: 用户时区信息. 为 None 时表示用户无时区信息(可能接口不支持)
    :param tenant_id: 用户所属租户 ID. 为 None 时表示用户无租户信息(可能接口不支持)
    """

    bk_username: str
    display_name: str
    time_zone: str | None = None
    tenant_id: str | None = None


class AbstractRequestBackend:
    def request_user_account(self, **credentials: Any) -> UserAccount:
        """Get user account through credentials

        :raises ServiceError: When the backend service is not available.
        :raises ResponseError: When the backend response status code is not in the 20x range, nor 403.
        :raises AccessPermissionDenied: When the user does not have access permission.
        :raises InvalidTokenCredentialsError: When invalid credentials are provided.
        """
        if bkauth_settings.USER_INFO_APIGW_URL:
            return self._request_apigw(**credentials)

        return self._request_esb(**credentials)

    async def async_request_user_account(self, **credentials: Any) -> UserAccount:
        """Asynchronous version of :meth:`request_user_account`."""
        if bkauth_settings.USER_INFO_APIGW_URL:
            return await self._async_request_apigw(**credentials)

        return await self._async_request_esb(**credentials)

    @staticmethod
    @abstractmethod
    def _request_apigw(**credentials: Any) -> UserAccount:
        """get user account by apigw"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _request_esb(**credentials: Any) -> UserAccount:
        """get user account by esb"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def _async_request_apigw(**credentials: Any) -> UserAccount:
        """Asynchronously get user account by APIGW."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def _async_request_esb(**credentials: Any) -> UserAccount:
        """Asynchronously get user account by ESB."""
        raise NotImplementedError


class TokenRequestBackend(AbstractRequestBackend):
    provider_type = ProviderType.BK

    @staticmethod
    def _get_apigw_request_params(credentials: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return bkauth_settings.USER_INFO_APIGW_URL, {
            "timeout": 10,
            "headers": {
                "blueking-language": get_language(),
                "X-Bkapi-Authorization": json.dumps(get_app_credentials()),
                # 全租户应用，调用全租户网关时，网关会强制要求传递 X-Bk-Tenant-Id, 但不会实际校验值的有效性, 统一传 default
                "X-Bk-Tenant-Id": "default",
            },
            "params": credentials,
        }

    @staticmethod
    def _parse_apigw_response(resp: Any) -> UserAccount:
        resp_json = resp_to_json(resp)

        if not isinstance(resp_json, dict):
            raise ValueError(f"response type expect dict, got: {resp_json}")  # noqa: TRY004

        if resp.status_code == 200:
            bk_username = resp_json["data"]["bk_username"]
            return UserAccount(
                bk_username=bk_username,
                display_name=resp_json["data"].get("display_name") or bk_username,
                time_zone=resp_json["data"].get("time_zone"),
                tenant_id=resp_json["data"].get("tenant_id"),
            )

        if resp.status_code == 403:
            raise AccessPermissionDenied(resp_json["error"]["message"])

        raise ResponseError(resp_json["error"]["message"])

    @staticmethod
    def _request_apigw(**credentials: Any) -> UserAccount:
        url, request_kwargs = TokenRequestBackend._get_apigw_request_params(credentials)
        try:
            resp = http_get(url, **request_kwargs)
        except HttpRequestError:
            raise ServiceError("Unable to request services") from None

        return TokenRequestBackend._parse_apigw_response(resp)

    @staticmethod
    async def _async_request_apigw(**credentials: Any) -> UserAccount:
        url, request_kwargs = TokenRequestBackend._get_apigw_request_params(credentials)
        try:
            resp = await async_http_get(url, **request_kwargs)
        except HttpRequestError:
            raise ServiceError("Unable to request services") from None

        return TokenRequestBackend._parse_apigw_response(resp)

    @staticmethod
    def _get_esb_request_params(credentials: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return bkauth_settings.USER_COOKIE_VERIFY_URL, {
            "timeout": 10,
            "headers": {
                "blueking-language": get_language(),
                "X-Bkapi-Authorization": json.dumps(dict(credentials, **get_app_credentials())),
            },
            "params": credentials,
        }

    @staticmethod
    def _parse_esb_response(resp: Any, credentials: dict[str, Any]) -> UserAccount:
        resp_json = resp_to_json(resp)

        if not isinstance(resp_json, dict):
            raise ValueError(f"response type expect dict, got: {resp_json}")  # noqa: TRY004

        # API 返回格式为：{"result": true, "code": 0, "message": "", "data": {"bk_username": "xxx"}}
        code = resp_json.get("code")
        if code == 0:
            username = resp_json["data"]["bk_username"]
            return UserAccount(bk_username=username, display_name=username)

        logger.debug(
            f"Get user fail, url: {bkauth_settings.USER_COOKIE_VERIFY_URL}, "
            f"params: {scrub_data(credentials)}, response: {resp_json}"
        )

        # 用户认证成功，但用户无应用访问权限
        if code == ACCESS_PERMISSION_DENIED_CODE:
            raise AccessPermissionDenied(resp_json.get("message"))

        raise InvalidTokenCredentialsError("Invalid credentials given")

    @staticmethod
    def _request_esb(**credentials: Any) -> UserAccount:
        url, request_kwargs = TokenRequestBackend._get_esb_request_params(credentials)
        try:
            resp = http_get(url, **request_kwargs)
        except HttpRequestError:
            raise ServiceError("unable to fetch token services") from None

        return TokenRequestBackend._parse_esb_response(resp, credentials)

    @staticmethod
    async def _async_request_esb(**credentials: Any) -> UserAccount:
        url, request_kwargs = TokenRequestBackend._get_esb_request_params(credentials)
        try:
            resp = await async_http_get(url, **request_kwargs)
        except HttpRequestError:
            raise ServiceError("unable to fetch token services") from None

        return TokenRequestBackend._parse_esb_response(resp, credentials)


class RequestBackend(AbstractRequestBackend):
    provider_type = ProviderType.RTX

    @staticmethod
    def _get_esb_request_params(credentials: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        return bkauth_settings.USER_COOKIE_VERIFY_URL, {"params": credentials, "timeout": 10}

    @staticmethod
    def _parse_esb_response(resp: Any, credentials: dict[str, Any]) -> UserAccount:
        resp_json = resp_to_json(resp)

        if not isinstance(resp_json, dict):
            raise ValueError(f"response type expect dict, got: {resp_json}")  # noqa: TRY004

        # API 返回格式为：{"msg": "", "data": {"username": "xxx"}, "ret": 0}
        if resp_json.get("ret") != 0:
            logger.debug(
                f"Get user fail, url: {bkauth_settings.USER_COOKIE_VERIFY_URL}, "
                f"params: {scrub_data(credentials)}, response: {resp_json}"
            )
            raise InvalidTokenCredentialsError("Invalid credentials given")

        username = resp_json["data"]["username"]
        return UserAccount(bk_username=username, display_name=username)

    @staticmethod
    def _request_esb(**credentials: Any) -> UserAccount:
        url, request_kwargs = RequestBackend._get_esb_request_params(credentials)
        try:
            resp = http_get(url, **request_kwargs)
        except HttpRequestError:
            raise ServiceError("unable to fetch token services") from None

        return RequestBackend._parse_esb_response(resp, credentials)

    @staticmethod
    async def _async_request_esb(**credentials: Any) -> UserAccount:
        url, request_kwargs = RequestBackend._get_esb_request_params(credentials)
        try:
            resp = await async_http_get(url, **request_kwargs)
        except HttpRequestError:
            raise ServiceError("unable to fetch token services") from None

        return RequestBackend._parse_esb_response(resp, credentials)

    @staticmethod
    def _request_apigw(**credentials: Any) -> UserAccount:
        raise NotImplementedError("No APIGW for RTX Backend")

    @staticmethod
    async def _async_request_apigw(**credentials: Any) -> UserAccount:
        raise NotImplementedError("No APIGW for RTX Backend")


class LoginToken:
    """Access token object"""

    token_timeout_margin = 300
    _json_fields: ClassVar[tuple[str, ...]] = (
        "login_token",
        "expires_at",
        "issued_at",
        "user_info",
    )

    login_token: str
    expires_at: datetime.datetime
    issued_at: datetime.datetime
    user_info: UserInfo

    def __init__(self, login_token: str, expires_in: int) -> None:
        assert login_token, "Must provide token string"
        assert expires_in, "Must provide expires_in seconds"
        self.login_token = login_token
        self.expires_at = now() + datetime.timedelta(seconds=expires_in)
        self.issued_at = now()
        self.user_info = UserInfo(username="AnonymousUser")

    def __str__(self) -> str:
        return "token: {} expires_at: {}".format(self.login_token, self.expires_at)

    def expired(self) -> bool:
        return self.expires_at < now()

    def make_user(self, provider_type: ProviderType | int) -> User:
        self.user_info.provider_type = ProviderType(provider_type)
        return create_user_from_token(self)

    def dump_json(self) -> str:
        """Serialize the token to JSON string."""
        user_info_type = type(self.user_info).__name__
        if user_info_type not in _USER_INFO_TYPES:
            raise TypeError(f"unsupported user info type: {user_info_type}")

        payload: dict[str, Any] = {}
        for field in self._json_fields:
            value = getattr(self, field)
            match field:
                case "expires_at" | "issued_at":
                    value = serialize_datetime(value)
                case "user_info":
                    value = json.loads(value.dump_json())
            payload[field] = value

        payload[_USER_INFO_TYPE_FIELD] = user_info_type
        return json.dumps(payload)

    @classmethod
    def parse_json(cls, payload: str | dict[str, Any]) -> LoginToken:
        """Parse the token from JSON string or dict."""
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict):
            raise TypeError(f"serialized payload must be dict, got: {type(payload)!r}")

        user_info_type = payload.get(_USER_INFO_TYPE_FIELD)
        if user_info_type not in _USER_INFO_TYPES:
            raise ValueError(f"unexpected serialized type: {user_info_type!r}")

        # Bypass __init__ so the original issued/expires timestamps survive the round trip.
        token = cls.__new__(cls)
        for field in cls._json_fields:
            value = payload[field]
            match field:
                case "expires_at" | "issued_at":
                    value = deserialize_datetime(value)
                case "user_info":
                    value = _USER_INFO_TYPES[user_info_type].parse_json(value)
            setattr(token, field, value)
        return token


def mocked_create_user_from_token(
    token: LoginToken,
    provider_type: ProviderType | int = ProviderType.RTX,
    username: str = bkauth_settings.MOCKED_USER_NAME,
) -> User:
    """Mocked create_user function, only for temporary use"""
    if provider_type == ProviderType.RTX:
        token.user_info = RtxUserInfo(
            LoginName=username,
            ChineseName=username,
        )
    elif provider_type == ProviderType.BK:
        token.user_info = BkUserInfo(bk_username=username, chname=username, email="", phone="")
    else:
        raise ValueError("Invalid provider_type given.")
    return create_user_from_token(token)


def create_user_from_token(token: LoginToken) -> User:
    """Create a user object from user info dict"""
    user = User(token=token)
    return token.user_info.provide(user)
