# -*- coding: utf-8 -*-
import string
from contextlib import contextmanager

import pytest
from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.token import LoginToken
from bkpaas_auth.middlewares import CookieLoginMiddleware, auth
from bkpaas_auth.models import User
from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.utils import override_settings
from mock import MagicMock, patch
from tests.utils import generate_random_string


@pytest.fixture
def bk_token():
    return str(int(generate_random_string(length=6, chars=string.digits)))


@pytest.fixture
def username():
    return str(int(generate_random_string(length=6, chars=string.digits)))


@pytest.fixture
def dj_request(rf, bk_token):
    request = rf.get('/')
    SessionMiddleware().process_request(request)
    AuthenticationMiddleware().process_request(request)
    request.COOKIES['bk_token'] = bk_token
    return request


def create_uin_user(uin):
    token = LoginToken('token', expires_in=86400)
    user = User(token=token, provider_type=ProviderType.BK, username=uin)
    user.email = "dummy"
    user.backend = "bkpaas_auth.backends.UniversalAuthBackend"
    return user


class TestCookieLoginMiddleware:
    @contextmanager
    def login_by_credentials(self, dj_request):
        """Login by given credentials, always success."""
        middleware = CookieLoginMiddleware(MagicMock())
        with patch.object(auth, 'authenticate') as mocked_authenticate:
            mocked_authenticate.return_value = create_uin_user(dj_request.COOKIES['bk_token'])
            middleware(dj_request)
            yield mocked_authenticate

    def test_no_credentials(self, db, dj_request):
        dj_request.COOKIES = {}
        middleware = CookieLoginMiddleware(MagicMock())
        with patch.object(middleware, 'authenticate_and_login') as mocked_auth_login:
            middleware(dj_request)

            assert not mocked_auth_login.called
            assert dj_request.session.get(SESSION_KEY) is None
            assert isinstance(dj_request.user, AnonymousUser)

    def test_fresh_login(self, db, dj_request, bk_token):
        with self.login_by_credentials(dj_request) as mocked_authenticate:
            assert mocked_authenticate.called
            assert mocked_authenticate.call_args[1]['auth_credentials'] == {'bk_token': bk_token}
            # Assert user session id has been written to session
            assert dj_request.session.get(SESSION_KEY) is not None
            assert isinstance(dj_request.user, User)

    def test_logout_when_credentials_empty(self, db, dj_request):
        with self.login_by_credentials(dj_request):
            # Assert login succeeded
            assert dj_request.session.get(SESSION_KEY) is not None

            del dj_request.COOKIES['bk_token']
            CookieLoginMiddleware(MagicMock())(dj_request)

            # Make sure logout succeeded
            assert dj_request.session.get(SESSION_KEY) is None
            assert isinstance(dj_request.user, AnonymousUser)

    def test_loginout_when_credentials_changed(self, db, dj_request):
        with self.login_by_credentials(dj_request):
            # Assert login succeeded
            assert dj_request.session.get(SESSION_KEY) is not None

        # Change credentials
        dj_request.COOKIES['bk_token'] = 'changed_skey_1'
        CookieLoginMiddleware(MagicMock())(dj_request)

        # Make sure logout succeeded
        assert dj_request.session.get(SESSION_KEY) is None
        assert isinstance(dj_request.user, AnonymousUser)

    def test_not_re_authenticate(self, db, dj_request):
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
        with patch.object(middleware, 'authenticate_and_login') as mocked_auth_login, patch(
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
            middleware, 'authenticate_and_login'
        ) as mocked_auth_login:
            middleware(dj_request)

            assert mocked_auth_login.called


class TestCookieLoginMiddlewareWithDjangoUser:
    @override_settings(AUTHENTICATION_BACKENDS=["bkpaas_auth.backends.DjangoAuthUserCompatibleBackend"])
    def test_auth(self, db, bk_token, dj_request):
        """Login by given credentials, always success."""
        middleware = CookieLoginMiddleware(MagicMock())
        dj_request.COOKIES['bk_token'] = bk_token

        with patch("bkpaas_auth.backends.UniversalAuthBackend.authenticate") as mocked_authenticate:
            mocked_authenticate.return_value = create_uin_user(bk_token)
            middleware(dj_request)

        UserModel = get_user_model()
        user = UserModel.objects.get(username=bk_token)
        assert user.username == bk_token
        assert user == dj_request.user
        assert isinstance(user, UserModel)
        assert not isinstance(user, User)
        assert isinstance(user.pk, int)
