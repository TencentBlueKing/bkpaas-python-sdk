# -*- coding: utf-8 -*-
import mock
import pytest
from django.test.utils import override_settings

from bkpaas_auth.backends import APIGatewayAuthBackend, UniversalAuthBackend
from bkpaas_auth.core.constants import ProviderType
from tests.utils import generate_random_string, mock_json_response, mock_raw_response


class TestUniversalAuthBackend:
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_ticket")
    @mock.patch("requests.Session.request")
    def test_authenticate_bk_ticket(self, mock_request, mocker):
        mock_request.return_value = mock_json_response({"msg": "", "data": {"username": "foo"}, "ret": 0})

        user = UniversalAuthBackend().authenticate(
            request=mocker.MagicMock(), auth_credentials={"bk_ticket": generate_random_string()}
        )

        assert user
        assert not user.is_anonymous
        assert user.is_authenticated
        assert user.username == "foo"
        assert getattr(user, "display_name") == "foo"

    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_token")
    @mock.patch("requests.Session.request")
    def test_authenticate_bk_token(self, mock_request, mocker):
        mock_request.return_value = mock_json_response(
            {"result": True, "code": 0, "message": "", "data": {"bk_username": "bar"}}
        )

        user = UniversalAuthBackend().authenticate(
            request=mocker.MagicMock(), auth_credentials={"bk_token": generate_random_string()}
        )

        assert user
        assert not user.is_anonymous
        assert user.is_authenticated
        assert user.username == "bar"
        assert getattr(user, "display_name") == "bar"

    @override_settings(
        BKAUTH_ENABLE_MULTI_TENANT_MODE=True,
        BKAUTH_BACKEND_TYPE="bk_token",
        BKAUTH_USER_INFO_APIGW_URL="fake_url",
    )
    @mock.patch("requests.Session.request")
    def test_authenticate_bk_token_for_tenant_mode(self, mock_request, mocker):
        """Test basic fields validation for tenant mode authentication"""
        mock_request.return_value = mock_raw_response(
            {
                "data": {
                    "bk_username": "5461b239-5ef2-4c81-a682-5907dbd5f394",
                    "tenant_id": "system",
                    "display_name": "foo",
                    "language": "zh-cn",
                }
            }
        )

        user = UniversalAuthBackend().authenticate(
            request=mocker.MagicMock(), auth_credentials={"bk_token": generate_random_string()}
        )

        assert user
        assert not user.is_anonymous
        assert user.is_authenticated
        assert user.username == "5461b239-5ef2-4c81-a682-5907dbd5f394"
        assert getattr(user, "display_name") == "foo"
        assert getattr(user, "tenant_id") == "system"

    @override_settings(
        BKAUTH_ENABLE_MULTI_TENANT_MODE=True,
        BKAUTH_BACKEND_TYPE="bk_token",
        BKAUTH_USER_INFO_APIGW_URL="fake_url",
    )
    @pytest.mark.parametrize(
        ("api_time_zone", "expected_time_zone"),
        [
            # Valid time zones
            ("Asia/Shanghai", "Asia/Shanghai"),
            ("UTC", "UTC"),
            ("Asia/Tokyo", "Asia/Tokyo"),
            # Missing time_zone field
            (None, None),
        ],
    )
    @mock.patch("requests.Session.request")
    def test_authenticate_bk_token_for_tenant_mode_time_zone(
        self, mock_request, mocker, api_time_zone, expected_time_zone
    ):
        """Test time_zone field handling in tenant mode authentication"""
        response_data = {
            "data": {
                "bk_username": "test_user",
                "tenant_id": "system",
                "display_name": "test",
                "language": "zh-cn",
            }
        }
        if api_time_zone is not None:
            response_data["data"]["time_zone"] = api_time_zone

        mock_request.return_value = mock_raw_response(response_data)

        user = UniversalAuthBackend().authenticate(
            request=mocker.MagicMock(), auth_credentials={"bk_token": generate_random_string()}
        )

        assert getattr(user, "time_zone") == expected_time_zone

class TestAPIGatewayAuthBackend:
    @pytest.fixture()
    def backend(self):
        return APIGatewayAuthBackend()

    @override_settings(BKAUTH_DEFAULT_PROVIDER_TYPE="RTX")
    def test_get_provider_type_default_value(self, backend):
        assert backend.get_provider_type() == ProviderType.RTX

    @override_settings(BKAUTH_DEFAULT_PROVIDER_TYPE="BK")
    def test_get_provider_type(self, backend):
        assert backend.get_provider_type() == ProviderType.BK

    def test_authenticate_not_verified(self, mocker, backend):
        user = backend.authenticate(
            request=mocker.MagicMock(),
            gateway_name="test",
            bk_username="admin",
            verified=False,
        )

        assert user.is_anonymous
        assert not user.is_authenticated
        assert user.username == "admin"

    def test_authenticate_verified(self, mocker, backend):
        user = backend.authenticate(
            request=mocker.MagicMock(),
            gateway_name="test",
            bk_username="admin",
            verified=True,
        )

        assert not user.is_anonymous
        assert user.is_authenticated
        assert user.username == "admin"

    def test_authenticate_with_additional_params(self, mocker, backend):
        """测试带多个额外参数的情况"""
        user = backend.authenticate(
            request=mocker.MagicMock(),
            gateway_name="test",
            bk_username="multi_param_user",
            verified=True,
            param1="value1",
            param2=2,
            param3={"key": "value"},
        )

        assert not user.is_anonymous
        assert user.is_authenticated
        assert user.username == "multi_param_user"
