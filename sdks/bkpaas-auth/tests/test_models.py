# -*- coding: utf-8 -*-
from unittest import mock

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.services import get_rtx_user_info
from bkpaas_auth.core.token import LoginToken
from bkpaas_auth.models import User
from django.conf import settings
from tests.utils import mock_json_response


class TestUser:
    def test_user_authenticated(self):
        user = User(token=None, provider_type=ProviderType.UIN, username='382238495')
        assert user.is_authenticated is False
        assert user.is_anonymous is True

        expired_token = LoginToken('token', expires_in=-1)
        user = User(token=expired_token, provider_type=ProviderType.UIN, username='382238495')
        assert user.is_authenticated is False
        assert user.is_anonymous is True

        token = LoginToken('token', expires_in=86400)
        user = User(token=token, provider_type=ProviderType.UIN, username='382238495')
        assert user.is_authenticated is True
        assert user.is_anonymous is False

    def test_user_info(self, get_rtx_user_info_response):
        with mock.patch('requests.Session.request') as mocked_request:
            mocked_request.return_value = mock_json_response(get_rtx_user_info_response)

            token = LoginToken('token', expires_in=86400)
            user_info = get_rtx_user_info(username=settings.USER_NAME)
            assert user_info.username == settings.USER_NAME
            assert user_info.chinese_name == settings.USER_NICKNAME

            user = User(token)
            user_info.provide(user)
            assert user.bkpaas_user_id == settings.USER_ID
            assert user.email == f'{settings.USER_NAME}@tencent.com'
            assert user.username == settings.USER_NAME
            assert user.chinese_name == settings.USER_NICKNAME
