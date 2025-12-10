# -*- coding: utf-8 -*-
from unittest import mock

import pytest
from django.conf import settings

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.services import get_rtx_user_info
from bkpaas_auth.core.token import LoginToken
from bkpaas_auth.models import User
from tests.utils import mock_json_response


class TestUser:
    def test_user_authenticated(self):
        user = User(token=None, provider_type=ProviderType.UIN, username='12345')
        assert user.is_authenticated is False
        assert user.is_anonymous is True

        expired_token = LoginToken('token', expires_in=-1)
        user = User(token=expired_token, provider_type=ProviderType.UIN, username='12345')
        assert user.is_authenticated is False
        assert user.is_anonymous is True

        token = LoginToken('token', expires_in=86400)
        user = User(token=token, provider_type=ProviderType.UIN, username='12345')
        assert user.is_authenticated is True
        assert user.is_anonymous is False

    def test_user_info(self, get_rtx_user_info_response):
        """Test base user info fields mapping from RTX user info"""
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

    @mock.patch('django.core.cache.cache.set')
    @mock.patch('django.core.cache.cache.get', return_value=None)
    @pytest.mark.parametrize(
        ("api_time_zone", "expected_time_zone"),
        [
            # Valid IANA time zones
            ("Asia/Shanghai", "Asia/Shanghai"),
            ("UTC", "UTC"),
            # Missing time_zone field
            (None, None),
        ],
    )
    def test_user_info_time_zone(
        self, _mock_cache_get, _mock_cache_set, get_rtx_user_info_response, api_time_zone, expected_time_zone
    ):
        """Test time_zone field handling with various values"""
        with mock.patch('requests.Session.request') as mocked_request:
            response_data = get_rtx_user_info_response.copy()
            if api_time_zone is None:
                response_data.pop("time_zone", None)
            else:
                response_data["time_zone"] = api_time_zone

            mocked_request.return_value = mock_json_response(response_data)

            user_info = get_rtx_user_info(username=settings.USER_NAME)
            assert user_info.time_zone == expected_time_zone

            token = LoginToken('token', expires_in=86400)
            user = User(token)
            user_info.provide(user)
            assert user.time_zone == expected_time_zone
