# -*- coding: utf-8 -*-
import mock
import pytest
from django.conf import settings

from bkpaas_auth import get_user_by_user_id
from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.services import get_bk_user_info
from bkpaas_auth.core.token import LoginToken, create_user_from_token
from bkpaas_auth.core.user_info import BkUserInfo
from bkpaas_auth.models import User
from tests.utils import mock_json_response


@pytest.fixture(autouse=True)
def use_bk_token_settings(settings):
    settings.BKAUTH_BACKEND_TYPE = 'bk_token'
    settings.USER_ID = '0335cce79c92'
    settings.USER_NAME = 'admin'
    settings.USER_NICKNAME = 'admin的中文名'


class TestMisc:
    @mock.patch('requests.Session.request')
    def test_get_user_by_user_id(self, mocked_request):
        mocked_request.return_value = mock_json_response(
            {
                "message": "",
                "code": 0,
                "data": {
                    "bk_username": settings.USER_NAME,
                    "chname": settings.USER_NICKNAME,
                    "email": "",
                    "phone": "",
                },
                "request_id": "ed3c8f75-d956-4dcd-b5d0-7bcd6c2e386a",
            }
        )
        user = get_user_by_user_id(settings.USER_ID, username_only=True)
        assert user.username == settings.USER_NAME
        assert not user.nickname

        user = get_user_by_user_id(settings.USER_ID, username_only=False)
        assert user.username == settings.USER_NAME
        assert user.nickname == settings.USER_NICKNAME


class TestUser:
    @mock.patch('requests.Session.request')
    def test_user_info(self, mocked_request):
        token = LoginToken('token', expires_in=86400)
        mocked_request.return_value = mock_json_response(
            {
                "message": "",
                "code": 0,
                "data": {
                    "bk_username": settings.USER_NAME,
                    "chname": settings.USER_NICKNAME,
                    "email": "",
                    "phone": "",
                },
                "request_id": "ed3c8f75-d956-4dcd-b5d0-7bcd6c2e386a",
            }
        )
        user_info = get_bk_user_info(username=settings.USER_NAME)
        assert user_info.username == settings.USER_NAME
        assert user_info.chinese_name == settings.USER_NICKNAME

        user = User(token)
        user_info.provide(user)
        assert user.bkpaas_user_id == settings.USER_ID
        assert user.email == ''
        assert user.username == settings.USER_NAME
        assert user.chinese_name == settings.USER_NICKNAME


class TestToken:
    @mock.patch('requests.Session.request')
    def test_create_user_from_token(self, mocked_request):
        token = LoginToken('token3', expires_in=3600)

        token.user_info = BkUserInfo(bk_username=settings.USER_NAME, chname='', email='', phone='')
        user = create_user_from_token(token)
        assert user.provider_type == ProviderType.BK
        assert user.username == settings.USER_NAME
