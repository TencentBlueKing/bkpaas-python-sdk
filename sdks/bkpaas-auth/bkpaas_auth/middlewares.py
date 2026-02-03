# -*- coding: utf-8 -*-
import json
import logging
import pickle
import time
from typing import Dict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.contrib import auth
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_str
from django.utils import timezone as dj_timezone

from bkpaas_auth.backends import UniversalAuthBackend
from bkpaas_auth.core.constants import ACCESS_PERMISSION_DENIED_CODE
from bkpaas_auth.core.exceptions import AccessPermissionDenied

logger = logging.getLogger(__name__)


class CookieLoginMiddleware(MiddlewareMixin):
    """Call auth.login when user credential cookies changes"""

    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The CookieLoginMiddleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE%s setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'bkpaas_auth.middlewares.CookieLoginMiddleware'."
        ) % ("_CLASSES" if settings.MIDDLEWARE is None else "")

        backend = UniversalAuthBackend()
        credentials = backend.get_credentials(request)

        # No credentials, call logout
        if not credentials:
            auth.logout(request)
            return self.get_response(request)

        if self.should_authenticate(request, backend, credentials):
            try:
                self.authenticate_and_login(request, credentials)
            except AccessPermissionDenied as e:
                resp = HttpResponse(
                    json.dumps({'code': ACCESS_PERMISSION_DENIED_CODE, 'detail': str(e)}),
                    content_type="application/json",
                )
                resp.status_code = 403
                return resp

        return self.get_response(request)

    def should_authenticate(
        self, request: HttpRequest, backend: UniversalAuthBackend, credentials: Dict[str, str]
    ) -> bool:
        """Decide whether to re-authenticate current credentials or not"""
        # Force re-login if credentials is different from last time
        credentials_been_modified = credentials != request.session.get('auth_credentials', {})
        if credentials_been_modified:
            return True

        # Force re-login if token is empty or obsolete
        token = backend.get_token_from_session(request)
        return token is None

    def authenticate_and_login(self, request: HttpRequest, credentials: Dict[str, str]):
        """Authenticate given credentials and do login(or logout if credentials is invalid)

        :params request: Current request object
        :params credentials: user credentials, such as uin/skey pair
        """
        logger.debug('Authenticating credentials...')
        user = auth.authenticate(request=request, auth_credentials=credentials)
        if user is None or not user.is_authenticated:
            logger.info('Authentication failed, logout.')
            auth.logout(request)
            return

        backend = auth.load_backend(user.backend)
        if not isinstance(backend, UniversalAuthBackend):
            logger.info("User is not validate by UniversalAuthBackend, skip login processes.")
            return

        logger.debug('Authentication finished, username: %s', user.username)
        request.session['provider_type'] = user.provider_type.value
        request.session['bkpaas_user_id'] = user.bkpaas_user_id
        request.session['bkpaas_authenticated_at'] = time.time()
        request.session['auth_credentials'] = credentials
        # python3 compatibility
        request.session['user_token'] = force_str(pickle.dumps(user.token), 'latin1')

        # Calling `auth.login` will rotate CSRF token and modify user session, only do this when the authenticated
        # user was different with the user stored in session. Otherwise CSRF token validation may fail due to the
        # rotation.
        if getattr(request, "user", None) != user:
            auth.login(request, user)


class UserTimezoneMiddleware(MiddlewareMixin):
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

    def process_request(self, request):
        # Ignore request without user attribute or anonymous user
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return

        user = request.user
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

    def process_response(self, request, response):
        """重置时区"""
        dj_timezone.deactivate()
        return response
