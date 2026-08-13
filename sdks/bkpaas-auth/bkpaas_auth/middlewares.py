# -*- coding: utf-8 -*-
import json
import logging
import time
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.contrib import auth
from django.http import HttpRequest, HttpResponse
from django.utils import timezone as dj_timezone
from django.utils.functional import SimpleLazyObject, empty

from bkpaas_auth.backends import UniversalAuthBackend
from bkpaas_auth.core.constants import ACCESS_PERMISSION_DENIED_CODE
from bkpaas_auth.core.exceptions import AccessPermissionDenied

logger = logging.getLogger(__name__)

GetResponse = Callable[[HttpRequest], Any | Awaitable[Any]]


class AuthenticationResult(Enum):
    """`CookieLoginMiddleware` 对认证结果的分类"""

    # 认证通过，且由 UniversalAuthBackend 完成，需要继续后续的登录流程
    VALID = "valid"
    # 认证失败，需要登出
    INVALID = "invalid"
    # 认证通过，但由其他 backend 完成，本中间件不介入
    UNSUPPORTED = "unsupported"


class CookieLoginMiddleware:
    """Call auth.login when user credential cookies changes"""

    sync_capable = True
    async_capable = True

    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(get_response)
        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request: HttpRequest) -> Any:
        if self.async_mode:
            return self.__acall__(request)

        response = self.process_request(request)
        if response is not None:
            return response
        return self.get_response(request)

    async def __acall__(self, request: HttpRequest) -> Any:
        response = await self.async_process_request(request)
        if response is not None:
            return response
        return await self.get_response(request)

    @staticmethod
    def _assert_session_middleware(request: HttpRequest) -> None:
        assert hasattr(request, "session"), (
            "The CookieLoginMiddleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'bkpaas_auth.middlewares.CookieLoginMiddleware'."
        )

    @staticmethod
    def _access_denied_response(exc: BaseException) -> HttpResponse:
        response = HttpResponse(
            json.dumps({"code": ACCESS_PERMISSION_DENIED_CODE, "detail": str(exc)}),
            content_type="application/json",
            status=403,
        )
        return response

    @staticmethod
    def _validate_authenticated_user(user: Any) -> AuthenticationResult:
        if user is None or not user.is_authenticated:
            logger.info("Authentication failed, logout.")
            return AuthenticationResult.INVALID

        backend = auth.load_backend(user.backend)
        if not isinstance(backend, UniversalAuthBackend):
            logger.info("User is not validate by UniversalAuthBackend, skip login processes.")
            return AuthenticationResult.UNSUPPORTED
        return AuthenticationResult.VALID

    @staticmethod
    def _get_session_data(user: Any, credentials: dict[str, str]) -> dict[str, Any]:
        return {
            "provider_type": user.provider_type.value,
            "bkpaas_user_id": user.bkpaas_user_id,
            "bkpaas_authenticated_at": time.time(),
            "auth_credentials": credentials,
            "user_token": user.token.dump_json(),
        }

    @staticmethod
    def _clear_async_user_cache(request: HttpRequest) -> None:
        if hasattr(request, "_acached_user"):
            del request._acached_user

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
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

    async def async_process_request(self, request: HttpRequest) -> HttpResponse | None:
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
        self, request: HttpRequest, backend: UniversalAuthBackend, credentials: dict[str, str]
    ) -> bool:
        """Decide whether to re-authenticate current credentials or not"""
        # Force re-login if credentials is different from last time
        if credentials != request.session.get("auth_credentials", {}):
            return True

        # Force re-login if token is empty or obsolete
        return backend.get_token_from_session(request) is None

    async def async_should_authenticate(
        self, request: HttpRequest, backend: UniversalAuthBackend, credentials: dict[str, str]
    ) -> bool:
        """Asynchronously decide whether the credentials need authentication."""
        if credentials != await request.session.aget("auth_credentials", {}):
            return True

        token = await backend.async_get_token_from_session(request)
        return token is None

    def authenticate_and_login(self, request: HttpRequest, credentials: dict[str, str]) -> None:
        """Authenticate given credentials and do login(or logout if credentials is invalid)

        :params request: Current request object
        :params credentials: user credentials, such as uin/skey pair
        """
        logger.debug("Authenticating credentials...")
        user = auth.authenticate(request=request, auth_credentials=credentials)
        authentication_result = self._validate_authenticated_user(user)
        if authentication_result == AuthenticationResult.INVALID:
            auth.logout(request)
            return
        if authentication_result == AuthenticationResult.UNSUPPORTED:
            return

        logger.debug("Authentication finished, username: %s", user.username)

        # Calling `auth.login` will rotate CSRF token and modify user session, only do this when the authenticated
        # user was different with the user stored in session. Otherwise CSRF token validation may fail due to the
        # rotation.
        #
        # NOTE: 必须先登录再写入 session 数据。当 session 中已存在其他用户时，`auth.login()`
        # 内部会调用 `session.flush()` 清空整个 session，若先写数据就会被一并清掉，导致
        # user_token / auth_credentials 丢失、每个请求都要重新认证。
        if getattr(request, "user", None) != user:
            auth.login(request, user)

        request.session.update(self._get_session_data(user, credentials))

    async def async_authenticate_and_login(self, request: HttpRequest, credentials: dict[str, str]) -> None:
        """Asynchronously authenticate credentials and log the user in or out."""
        logger.debug("Authenticating credentials...")
        user = await auth.aauthenticate(request=request, auth_credentials=credentials)
        authentication_result = self._validate_authenticated_user(user)
        if authentication_result == AuthenticationResult.INVALID:
            await auth.alogout(request)
            self._clear_async_user_cache(request)
            return
        if authentication_result == AuthenticationResult.UNSUPPORTED:
            return

        logger.debug("Authentication finished, username: %s", user.username)

        # NOTE: 与同步版本一样，必须先登录再写入 session 数据，避免 `auth.alogin()` 内部的
        # `session.aflush()` 把刚写入的数据清掉。
        current_user = await request.auser() if hasattr(request, "auser") else getattr(request, "user", None)
        if current_user != user:
            await auth.alogin(request, user)
            request._acached_user = user

        await request.session.aupdate(self._get_session_data(user, credentials))


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

    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(get_response)
        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request: HttpRequest) -> Any:
        if self.async_mode:
            return self.__acall__(request)

        self.process_request(request)
        response = self.get_response(request)
        return self.process_response(request, response)

    async def __acall__(self, request: HttpRequest) -> Any:
        await self.async_process_request(request)
        response = await self.get_response(request)
        return self.process_response(request, response)

    @staticmethod
    def _activate_user_timezone(user: Any) -> None:
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

    def process_request(self, request: HttpRequest) -> None:
        # Ignore request without user attribute or anonymous user
        self._activate_user_timezone(getattr(request, "user", None))

    async def async_process_request(self, request: HttpRequest) -> None:
        self._activate_user_timezone(await self._aresolve_user(request))

    @staticmethod
    async def _aresolve_user(request: HttpRequest) -> Any:
        """Resolve the current user for the async request chain.

        本中间件要求放在所有认证中间件之后，因此 `request.user` 才是认证链的最终结果，应当
        优先采用——有些认证中间件（如 apigw-manager 的 ApiGatewayJWTUserMiddleware）只写
        `request.user` 而不写 session，此时 `request.auser()` 从 session 还原出的用户是错的。

        但 `AuthenticationMiddleware` 写入的 `request.user` 是一个惰性对象，在异步链中直接读取
        会触发同步的 session / ORM 访问并抛出 SynchronousOnlyOperation，所以仅当它尚未求值时
        才改用 `request.auser()`（二者数据来源相同，都是 session）。

        已知限制: 若某个认证中间件写入的是尚未求值的惰性 `request.user`，这里仍会回退到
        `request.auser()`，取到的可能不是该中间件认证出的用户。
        """
        user = getattr(request, "user", None)
        if user is not None and not (isinstance(user, SimpleLazyObject) and user._wrapped is empty):
            return user

        if hasattr(request, "auser"):
            return await request.auser()
        return user

    def process_response(self, request: HttpRequest, response: Any) -> Any:
        """重置时区"""
        dj_timezone.deactivate()
        return response
