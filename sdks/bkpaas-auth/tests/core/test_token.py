# -*- coding: utf-8 -*-
from unittest import mock

from django.conf import settings
from django.test.utils import override_settings

from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.token import LoginToken, create_user_from_token, mocked_create_user_from_token
from bkpaas_auth.core.user_info import RtxUserInfo


class TestToken:
    @mock.patch("requests.Session.request")
    def test_create_user_from_token(self, mocked_request, get_rtx_user_info_response):
        with override_settings(BKAUTH_BACKEND_TYPE="bk_ticket"):
            token = LoginToken("token3", expires_in=3600)
            token.user_info = RtxUserInfo(
                LoginName=settings.USER_NAME,
                ChineseName=settings.USER_NAME,
            )
            user = create_user_from_token(token)
            assert user.provider_type == ProviderType.RTX
            assert user.username == settings.USER_NAME

    def test_mocked_create_user_from_token(self):
        token = LoginToken("token_string", expires_in=3600)
        assert mocked_create_user_from_token(token).username == bkauth_settings.MOCKED_USER_NAME
        assert mocked_create_user_from_token(token, username="test_name").username == "test_name"
