# -*- coding: utf-8 -*-
import json
import string
from contextlib import contextmanager
from typing import Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from asgiref.sync import iscoroutinefunction
from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from django.test.utils import override_settings
from django.utils import timezone as dj_timezone

from bkpaas_auth.backends import UniversalAuthBackend
from bkpaas_auth.core.constants import ACCESS_PERMISSION_DENIED_CODE, ProviderType
from bkpaas_auth.core.exceptions import AccessPermissionDenied
from bkpaas_auth.core.token import LoginToken
from bkpaas_auth.core.user_info import UserInfo
from bkpaas_auth.middlewares import CookieLoginMiddleware, UserTimezoneMiddleware, auth
from bkpaas_auth.models import User
from tests.utils import generate_random_string


@pytest.fixture
def bk_token():
    return str(int(generate_random_string(length=6, chars=string.digits)))


@pytest.fixture
def username():
    return str(int(generate_random_string(length=6, chars=string.digits)))


@pytest.fixture
def dj_request(rf, bk_token):
    req = rf.get("/")
    SessionMiddleware(MagicMock()).process_request(req)
    AuthenticationMiddleware(MagicMock()).process_request(req)
    req.COOKIES["bk_token"] = bk_token
    return req


def create_uin_user(uin):
    token = LoginToken("token", expires_in=86400)
    token.user_info = UserInfo(username=uin, display_name=uin)
    token.user_info.provider_type = ProviderType.BK
    user = User(token=token, provider_type=ProviderType.BK, username=uin)
    user.email = "dummy"
    user.backend = "bkpaas_auth.backends.UniversalAuthBackend"
    return user


class FakeCookieLoginMiddleware(CookieLoginMiddleware):
    def should_authenticate(
        self, request: HttpRequest, backend: UniversalAuthBackend, credentials: Dict[str, str]
    ) -> bool:
        return True

    def authenticate_and_login(self, request: HttpRequest, credentials: Dict[str, str]):
        raise AccessPermissionDenied("authenticated user has no access permissions")

    async def async_should_authenticate(
        self, request: HttpRequest, backend: UniversalAuthBackend, credentials: Dict[str, str]
    ) -> bool:
        return True

    async def async_authenticate_and_login(self, request: HttpRequest, credentials: Dict[str, str]):
        raise AccessPermissionDenied("authenticated user has no access permissions")


@pytest.mark.parametrize("middleware_class", [CookieLoginMiddleware, UserTimezoneMiddleware])
def test_middleware_supports_sync_and_async(middleware_class):
    assert middleware_class.sync_capable is True
    assert middleware_class.async_capable is True

    async def get_response(request):
        return HttpResponse("OK")

    assert iscoroutinefunction(middleware_class(get_response))


class TestCookieLoginMiddleware:
    @contextmanager
    def login_by_credentials(self, dj_request):
        """Login by given credentials, always success."""
        middleware = CookieLoginMiddleware(MagicMock())
        with patch.object(auth, "authenticate") as mocked_authenticate:
            mocked_authenticate.return_value = create_uin_user(dj_request.COOKIES["bk_token"])
            middleware(dj_request)
            yield mocked_authenticate

    def test_no_credentials(self, db, dj_request):
        dj_request.COOKIES = {}
        middleware = CookieLoginMiddleware(MagicMock())
        with patch.object(middleware, "authenticate_and_login") as mocked_auth_login:
            middleware(dj_request)

            assert not mocked_auth_login.called
            assert dj_request.session.get(SESSION_KEY) is None
            assert isinstance(dj_request.user, AnonymousUser)

    def test_authenticated_user_has_no_access_permissions(self, db, dj_request):
        middleware = FakeCookieLoginMiddleware(MagicMock())
        with patch("bkpaas_auth.backends.UniversalAuthBackend.get_credentials") as mocked_get_token:
            mocked_get_token.return_value = {"bk_token": dj_request.COOKIES["bk_token"]}
            resp = middleware.process_request(dj_request)

            assert resp.status_code == 403
            resp_data = json.loads(resp.content.decode("utf-8"))
            assert resp_data["code"] == ACCESS_PERMISSION_DENIED_CODE
            assert resp_data["detail"] == "authenticated user has no access permissions"

    def test_fresh_login(self, db, dj_request, bk_token):
        with self.login_by_credentials(dj_request) as mocked_authenticate:
            assert mocked_authenticate.called
            assert mocked_authenticate.call_args[1]["auth_credentials"] == {"bk_token": bk_token}
            # Assert user session id has been written to session
            assert dj_request.session.get(SESSION_KEY) is not None
            assert LoginToken.parse_json(dj_request.session["user_token"]).user_info.username == bk_token
            assert isinstance(dj_request.user, User)

    def test_logout_when_credentials_empty(self, db, dj_request):
        with self.login_by_credentials(dj_request):
            # Assert login succeeded
            assert dj_request.session.get(SESSION_KEY) is not None

            del dj_request.COOKIES["bk_token"]
            CookieLoginMiddleware(MagicMock())(dj_request)

            # Make sure logout succeeded
            assert dj_request.session.get(SESSION_KEY) is None
            assert isinstance(dj_request.user, AnonymousUser)

    def test_loginout_when_credentials_changed(self, db, dj_request):
        with self.login_by_credentials(dj_request):
            # Assert login succeeded
            assert dj_request.session.get(SESSION_KEY) is not None

        # Change credentials
        dj_request.COOKIES["bk_token"] = "changed_skey_1"
        with patch.object(auth, "authenticate", return_value=None):
            CookieLoginMiddleware(MagicMock())(dj_request)

        # Make sure logout succeeded
        assert dj_request.session.get(SESSION_KEY) is None
        assert isinstance(dj_request.user, AnonymousUser)

    def test_no_re_authenticate(self, db, dj_request):
        with self.login_by_credentials(dj_request) as mocked_authenticate:
            # Assert login succeeded
            assert dj_request.session.get(SESSION_KEY) is not None
            assert mocked_authenticate.called

            middleware = CookieLoginMiddleware(MagicMock())
            middleware(dj_request)

            assert mocked_authenticate.call_count == 1
            assert dj_request.session.get(SESSION_KEY) is not None
            assert isinstance(dj_request.user, User)

    def test_should_authenticate_when_token_is_empty(self, db, dj_request):
        with self.login_by_credentials(dj_request):
            # Assert login succeeded
            assert dj_request.session.get(SESSION_KEY) is not None

        middleware = CookieLoginMiddleware(MagicMock())
        with patch.object(middleware, "authenticate_and_login") as mocked_auth_login, patch(
            "bkpaas_auth.backends.UniversalAuthBackend.get_token_from_session"
        ) as mocked_get_token:
            mocked_get_token.return_value = None
            middleware(dj_request)

            assert mocked_auth_login.called

    def test_should_authenticate_after_session_timeout(self, db, dj_request):
        with self.login_by_credentials(dj_request):
            # Assert login succeeded
            assert dj_request.session.get(SESSION_KEY) is not None

        middleware = CookieLoginMiddleware(MagicMock())
        with override_settings(BKAUTH_SESSION_TIMEOUT=0), patch.object(
            middleware, "authenticate_and_login"
        ) as mocked_auth_login:
            middleware(dj_request)

            assert mocked_auth_login.called

    @pytest.mark.asyncio
    async def test_async_get_response_is_awaited(self, rf):
        request = rf.get("/")
        request.session = {}
        expected_response = HttpResponse("OK")

        async def get_response(request):
            return expected_response

        middleware = CookieLoginMiddleware(get_response)

        with patch.object(auth, "alogout", new_callable=AsyncMock):
            response = await middleware(request)

        assert response is expected_response

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_token")
    async def test_async_authentication_uses_native_async_http(self, dj_request, bk_token):
        async def get_response(request):
            return HttpResponse("OK")

        response = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"result": True, "code": 0, "message": "", "data": {"bk_username": bk_token}}),
        )
        with patch("bkpaas_auth.core.token.http_get", side_effect=AssertionError("sync HTTP must not be used")), patch(
            "bkpaas_auth.core.token.async_http_get", new_callable=AsyncMock, return_value=response
        ) as async_http_get:
            result = await CookieLoginMiddleware(get_response)(dj_request)

        assert result.status_code == 200
        assert await dj_request.session.aget(SESSION_KEY) is not None
        assert (await dj_request.auser()).username == bk_token
        async_http_get.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_async_access_denied_short_circuits_get_response(self, rf):
        request = rf.get("/")
        request.session = {}

        async def get_response(request):
            pytest.fail("get_response should not be called")

        middleware = FakeCookieLoginMiddleware(get_response)
        with patch.object(
            UniversalAuthBackend,
            "get_credentials",
            return_value={"bk_token": "token"},
        ):
            response = await middleware(request)

        assert response.status_code == 403
        assert json.loads(response.content)["code"] == ACCESS_PERMISSION_DENIED_CODE


class TestCookieLoginMiddlewareWithDjangoUser:
    @override_settings(AUTHENTICATION_BACKENDS=["bkpaas_auth.backends.DjangoAuthUserCompatibleBackend"])
    def test_auth(self, db, bk_token, dj_request):
        """Login by given credentials, always success."""
        middleware = CookieLoginMiddleware(MagicMock())
        dj_request.COOKIES["bk_token"] = bk_token

        with patch("bkpaas_auth.backends.UniversalAuthBackend.authenticate") as mocked_authenticate:
            mocked_authenticate.return_value = create_uin_user(bk_token)
            middleware(dj_request)

        UserModel = get_user_model()  # noqa: N806
        user = UserModel.objects.get(username=bk_token)
        assert user.username == bk_token
        assert user == dj_request.user
        assert isinstance(user, UserModel)
        assert not isinstance(user, User)
        assert isinstance(user.pk, int)

    @override_settings(
        AUTHENTICATION_BACKENDS=["bkpaas_auth.backends.DjangoAuthUserCompatibleBackend"],
        TIME_ZONE="UTC",
    )
    def test_time_zone_propagated_to_django_user(self, db, bk_token, dj_request):
        """time_zone should survive connect_to_django_user."""
        middleware = CookieLoginMiddleware(MagicMock())
        dj_request.COOKIES["bk_token"] = bk_token

        # Create a bkpaas_auth User with time_zone
        user = create_uin_user(bk_token)
        user.time_zone = "Asia/Shanghai"

        with patch("bkpaas_auth.backends.UniversalAuthBackend.authenticate") as mocked_authenticate:
            mocked_authenticate.return_value = user
            middleware(dj_request)

        # time_zone should be propagated from bkpaas_auth.User to Django AuthUser
        assert getattr(dj_request.user, "time_zone", None) == "Asia/Shanghai"

        # UserTimezoneMiddleware should activate the timezone
        tz_middleware = UserTimezoneMiddleware(MagicMock())
        dj_timezone.deactivate()
        tz_middleware.process_request(dj_request)
        assert dj_timezone.get_current_timezone_name() == "Asia/Shanghai"


class TestUserTimezoneMiddleware:
    """Test cases for UserTimezoneMiddleware"""

    @pytest.fixture
    def middleware(self):
        return UserTimezoneMiddleware(MagicMock())

    @pytest.fixture
    def authenticated_user(self):
        """Create a mock authenticated user"""
        user = MagicMock()
        user.is_authenticated = True
        return user

    @pytest.fixture(autouse=True)
    def setup_timezone(self):
        """Reset timezone before and after each test to avoid pollution"""
        with override_settings(TIME_ZONE="UTC"):
            dj_timezone.deactivate()
            yield
            dj_timezone.deactivate()

    def test_skip_request_without_user_attr(self, rf, middleware):
        """Test that requests without user attribute don't change timezone"""
        middleware.process_request(rf.get("/"))
        assert dj_timezone.get_current_timezone_name() == "UTC"

    def test_skip_anonymous_user(self, rf, middleware):
        """Test that anonymous users don't change timezone"""
        request = rf.get("/")
        request.user = AnonymousUser()
        middleware.process_request(request)
        assert dj_timezone.get_current_timezone_name() == "UTC"

    def test_activate_valid_user_timezone(self, rf, middleware, authenticated_user):
        """Test that valid user timezone is actually activated"""
        request = rf.get("/")
        authenticated_user.time_zone = "America/New_York"
        request.user = authenticated_user
        middleware.process_request(request)
        assert dj_timezone.get_current_timezone_name() == "America/New_York"

    def test_sync_get_response_uses_user_timezone_and_resets_it(self, rf, authenticated_user):
        request = rf.get("/")
        authenticated_user.time_zone = "America/New_York"
        request.user = authenticated_user
        expected_response = HttpResponse("OK")
        timezone_during_request = None

        def get_response(request):
            nonlocal timezone_during_request
            timezone_during_request = dj_timezone.get_current_timezone_name()
            return expected_response

        response = UserTimezoneMiddleware(get_response)(request)

        assert response is expected_response
        assert timezone_during_request == "America/New_York"
        assert dj_timezone.get_current_timezone_name() == "UTC"

    @pytest.mark.parametrize(
        ("time_zone_value", "has_attr"),
        [
            ("Invalid/Timezone", True),
            ("", True),
            (None, True),
            (None, False),
            (123, True),
        ],
        ids=["invalid_timezone", "empty_string", "none_value", "no_attr", "non_string_type"],
    )
    @override_settings(TIME_ZONE="Asia/Shanghai")
    def test_fallback_to_default_timezone(self, rf, middleware, authenticated_user, time_zone_value, has_attr):
        """Test fallback to default timezone for various edge cases"""
        request = rf.get("/")
        if has_attr:
            authenticated_user.time_zone = time_zone_value
        else:
            del authenticated_user.time_zone
        request.user = authenticated_user
        middleware.process_request(request)
        assert dj_timezone.get_current_timezone_name() == "Asia/Shanghai"

    @pytest.mark.asyncio
    async def test_async_get_response_uses_user_timezone_and_resets_it(self, rf, authenticated_user):
        request = rf.get("/")
        authenticated_user.time_zone = "America/New_York"
        request.user = authenticated_user
        expected_response = HttpResponse("OK")
        timezone_during_request = None

        async def get_response(request):
            nonlocal timezone_during_request
            timezone_during_request = dj_timezone.get_current_timezone_name()
            return expected_response

        middleware = UserTimezoneMiddleware(get_response)
        response = await middleware(request)

        assert response is expected_response
        assert timezone_during_request == "America/New_York"
        assert dj_timezone.get_current_timezone_name() == "UTC"

    @pytest.mark.asyncio
    async def test_async_get_response_resolves_user_with_auser(self, rf, authenticated_user):
        request = rf.get("/")
        authenticated_user.time_zone = "America/New_York"
        request.auser = AsyncMock(return_value=authenticated_user)
        timezone_during_request = None

        async def get_response(request):
            nonlocal timezone_during_request
            timezone_during_request = dj_timezone.get_current_timezone_name()
            return HttpResponse("OK")

        await UserTimezoneMiddleware(get_response)(request)

        request.auser.assert_awaited_once_with()
        assert timezone_during_request == "America/New_York"
