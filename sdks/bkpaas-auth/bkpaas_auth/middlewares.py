# -*- coding: utf-8 -*-
import json
import logging
import time
from typing import Dict

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.contrib import auth
from django.http import HttpRequest, HttpResponse
from django.utils import timezone as dj_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from bkpaas_auth.backends import UniversalAuthBackend
from bkpaas_auth.core.constants import ACCESS_PERMISSION_DENIED_CODE
from bkpaas_auth.core.exceptions import AccessPermissionDenied

logger = logging.getLogger(__name__)


class CookieLoginMiddleware:
    """Call auth.login when user credential cookies changes"""

    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(get_response)
        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request):
        if self.async_mode:
            return self.__acall__(request)

        response = self.process_request(request)
        if response is not None:
            return response
        return self.get_response(request)

    async def __acall__(self, request):
        response = await self.async_process_request(request)
        if response is not None:
            return response
        return await self.get_response(request)

    @staticmethod
    def _assert_session_middleware(request):
        assert hasattr(request, "session"), (
            "The CookieLoginMiddleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'bkpaas_auth.middlewares.CookieLoginMiddleware'."
        )

    @staticmethod
    def _access_denied_response(exc):
        response = HttpResponse(
            json.dumps({"code": ACCESS_PERMISSION_DENIED_CODE, "detail": str(exc)}),
            content_type="application/json",
            status=403,
        )
        return response

    @staticmethod
    def _should_authenticate(credentials, stored_credentials, token):
        return credentials != stored_credentials or token is None

    @staticmethod
    def _validate_authenticated_user(user):
        if user is None or not user.is_authenticated:
            logger.info("Authentication failed, logout.")
            return "invalid"

        backend = auth.load_backend(user.backend)
        if not isinstance(backend, UniversalAuthBackend):
            logger.info("User is not validate by UniversalAuthBackend, skip login processes.")
            return "unsupported"
        return "valid"

    @staticmethod
    def _get_session_data(user, credentials):
        return {
            "provider_type": user.provider_type.value,
            "bkpaas_user_id": user.bkpaas_user_id,
            "bkpaas_authenticated_at": time.time(),
            "auth_credentials": credentials,
            "user_token": user.token.dump_json(),
        }

    @staticmethod
    def _clear_async_user_cache(request):
        if hasattr(request, "_acached_user"):
            del request._acached_user

    def process_request(self, request):
        self._assert_session_middleware(request)

        backend = UniversalAuthBackend()
        credentials = backend.get_credentials(request)

        # No credentials, call logout
        if not credentials:
            auth.logout(request)
            return None

        if self.should_authenticate(request, backend, credentials):
            try:
                self.authenticate_and_login(request, credentials)
            except AccessPermissionDenied as e:
                return self._access_denied_response(e)

        return None

    async def async_process_request(self, request):
        """Asynchronous counterpart of :meth:`process_request`."""
        self._assert_session_middleware(request)

        backend = UniversalAuthBackend()
        credentials = backend.get_credentials(request)
        if not credentials:
            await auth.alogout(request)
            self._clear_async_user_cache(request)
            return None

        if await self.async_should_authenticate(request, backend, credentials):
            try:
                await self.async_authenticate_and_login(request, credentials)
            except AccessPermissionDenied as e:
                return self._access_denied_response(e)
        return None

    def should_authenticate(
        self, request: HttpRequest, backend: UniversalAuthBackend, credentials: Dict[str, str]
    ) -> bool:
        """Decide whether to re-authenticate current credentials or not"""
        # Force re-login if credentials is different from last time
        token = backend.get_token_from_session(request)
        return self._should_authenticate(credentials, request.session.get("auth_credentials", {}), token)

    async def async_should_authenticate(
        self, request: HttpRequest, backend: UniversalAuthBackend, credentials: Dict[str, str]
    ) -> bool:
        """Asynchronously decide whether the credentials need authentication."""
        stored_credentials = await request.session.aget("auth_credentials", {})
        token = await backend.async_get_token_from_session(request)
        return self._should_authenticate(credentials, stored_credentials, token)

    def authenticate_and_login(self, request: HttpRequest, credentials: Dict[str, str]):
        """Authenticate given credentials and do login(or logout if credentials is invalid)

        :params request: Current request object
        :params credentials: user credentials, such as uin/skey pair
        """
        logger.debug("Authenticating credentials...")
        user = auth.authenticate(request=request, auth_credentials=credentials)
        authentication_result = self._validate_authenticated_user(user)
        if authentication_result == "invalid":
            auth.logout(request)
            return
        if authentication_result == "unsupported":
            return

        logger.debug("Authentication finished, username: %s", user.username)
        request.session.update(self._get_session_data(user, credentials))

        # Calling `auth.login` will rotate CSRF token and modify user session, only do this when the authenticated
        # user was different with the user stored in session. Otherwise CSRF token validation may fail due to the
        # rotation.
        if getattr(request, "user", None) != user:
            auth.login(request, user)

    async def async_authenticate_and_login(self, request: HttpRequest, credentials: Dict[str, str]):
        """Asynchronously authenticate credentials and log the user in or out."""
        logger.debug("Authenticating credentials...")
        user = await auth.aauthenticate(request=request, auth_credentials=credentials)
        authentication_result = self._validate_authenticated_user(user)
        if authentication_result == "invalid":
            await auth.alogout(request)
            self._clear_async_user_cache(request)
            return
        if authentication_result == "unsupported":
            return

        logger.debug("Authentication finished, username: %s", user.username)
        await request.session.aupdate(self._get_session_data(user, credentials))

        current_user = await request.auser() if hasattr(request, "auser") else getattr(request, "user", None)
        if current_user != user:
            await auth.alogin(request, user)
            request._acached_user = user


class UserTimezoneMiddleware:
    """按用户的时区属性激活 Django 时区。

    该中间件从用户管理系统获取用户时区信息并激活，使所有时间相关的序列化输出
    都使用用户所在时区的偏移量。

    执行逻辑:
    1. 未登录用户跳过处理
    2. 从 request.user 读取 time_zone 属性
    3. 若时区字段缺失或非法，回退到默认时区 settings.TIME_ZONE
    4. 在响应返回时重置时区，避免线程复用导致的时区污染

    NOTE: 必须放在所有用户认证中间件之后
    """

    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(get_response)
        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request):
        if self.async_mode:
            return self.__acall__(request)

        self.process_request(request)
        response = self.get_response(request)
        return self.process_response(request, response)

    async def __acall__(self, request):
        await self.async_process_request(request)
        response = await self.get_response(request)
        return self.process_response(request, response)

    @staticmethod
    def _activate_user_timezone(user):
        if user is None or not user.is_authenticated:
            return

        tz_name = getattr(user, "time_zone", None)

        # Try to activate user's timezone if it's a non-empty string
        if tz_name and isinstance(tz_name, str):
            try:
                user_tz = ZoneInfo(tz_name)
                dj_timezone.activate(user_tz)
            except ZoneInfoNotFoundError as e:
                logger.warning(
                    "Invalid time_zone '%s' for user '%s', fallback to default. Error: %s",
                    tz_name,
                    user.username,
                    str(e),
                )
            else:
                logger.debug("Activated timezone '%s' for user '%s'", tz_name, user.username)
                return

        # Fallback to default timezone when time_zone is empty or invalid
        dj_timezone.activate(dj_timezone.get_default_timezone())

    def process_request(self, request):
        # Ignore request without user attribute or anonymous user
        self._activate_user_timezone(getattr(request, "user", None))

    async def async_process_request(self, request):
        """Resolve the current user without evaluating Django's sync lazy user."""
        if hasattr(request, "auser"):
            user = await request.auser()
        else:
            user = getattr(request, "user", None)
        self._activate_user_timezone(user)

    def process_response(self, request, response):
        """重置时区"""
        dj_timezone.deactivate()
        return response
