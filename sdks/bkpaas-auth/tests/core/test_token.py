# -*- coding: utf-8 -*-
import json
from unittest import mock

import pytest
from django.conf import settings
from django.test.utils import override_settings

from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.token import LoginToken, create_user_from_token, mocked_create_user_from_token
from bkpaas_auth.core.user_info import BkUserInfo, RtxUserInfo, UserInfo


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

    def test_user_info_json_round_trip(self):
        user_info = UserInfo(
            username="base-user",
            display_name="Base User",
            time_zone="Asia/Shanghai",
            tenant_id="system",
        )
        user_info.provider_type = ProviderType.BK

        payload = json.loads(user_info.dump_json())
        restored = UserInfo.parse_json(payload)

        assert type(restored) is UserInfo
        assert "_user_info_type" not in payload
        assert restored.username == user_info.username
        assert restored.display_name == user_info.display_name
        assert restored.time_zone == user_info.time_zone
        assert restored.tenant_id == user_info.tenant_id
        assert restored.provider_type == ProviderType.BK

    @pytest.mark.parametrize(
        "user_info",
        [
            UserInfo(
                username="base-user",
                display_name="Base User",
                time_zone="Asia/Shanghai",
                tenant_id="system",
            ),
            RtxUserInfo(
                LoginName="rtx-user",
                ChineseName="RTX User",
                MobilePhoneNumber="123456",
                time_zone="Asia/Shanghai",
                tenant_id="system",
            ),
            BkUserInfo(
                bk_username="bk-user",
                chname="BK User",
                email="bk-user@example.com",
                phone="654321",
                time_zone="UTC",
                tenant_id="system",
            ),
        ],
        ids=["base_user_info", "rtx_user_info", "bk_user_info"],
    )
    def test_login_token_json_round_trip(self, user_info):
        token = LoginToken("token", expires_in=86400)
        if type(user_info) is UserInfo:
            user_info.provider_type = ProviderType.BK
        token.user_info = user_info

        restored = LoginToken.parse_json(token.dump_json())

        assert restored.login_token == token.login_token
        assert restored.expires_at == token.expires_at
        assert restored.issued_at == token.issued_at
        assert isinstance(restored.user_info, type(user_info))
        assert restored.user_info == token.user_info

    def test_login_token_parse_json_rejects_invalid_payload(self):
        with pytest.raises(ValueError, match="unexpected serialized type"):
            LoginToken.parse_json(
                json.dumps(
                    {
                        "login_token": "token",
                        "expires_at": "2026-04-21T00:00:00+00:00",
                        "issued_at": "2026-04-20T00:00:00+00:00",
                        "_user_info_type": "NotUserInfo",
                        "user_info": {},
                    }
                )
            )
