# -*- coding: utf-8 -*-
import pickle
from unittest import mock

import pytest
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.test.utils import override_settings

from bkpaas_auth.backends import APIGatewayAuthBackend, DjangoAuthUserCompatibleBackend, UniversalAuthBackend
from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.token import LoginToken, UserAccount
from bkpaas_auth.core.user_info import UserInfo
from tests.utils import generate_random_string, mock_json_response, mock_raw_response


class TestUniversalAuthBackend:
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_ticket")
    @mock.patch("httpx2.Client.request")
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
    @mock.patch("httpx2.Client.request")
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

    @pytest.mark.asyncio
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_token")
    async def test_async_authenticate_uses_async_request_backend(self, mocker):
        backend = UniversalAuthBackend()
        sync_request = mocker.patch.object(
            backend.request_backend,
            "request_user_account",
            side_effect=AssertionError("sync request backend must not be used"),
        )
        async_request = mocker.patch.object(
            backend.request_backend,
            "async_request_user_account",
            new=mocker.AsyncMock(return_value=UserAccount(bk_username="async-user", display_name="Async User")),
        )

        user = await backend.aauthenticate(request=mocker.MagicMock(), auth_credentials={"bk_token": "token"})

        assert user is not None
        assert user.username == "async-user"
        assert user.display_name == "Async User"
        async_request.assert_awaited_once_with(bk_token="token")
        sync_request.assert_not_called()

    @override_settings(
        BKAUTH_ENABLE_MULTI_TENANT_MODE=True,
        BKAUTH_BACKEND_TYPE="bk_token",
        BKAUTH_USER_INFO_APIGW_URL="fake_url",
    )
    @mock.patch("httpx2.Client.request")
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
    @mock.patch("httpx2.Client.request")
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

    @override_settings(BKAUTH_BACKEND_TYPE="bk_token")
    def test_get_token_from_session(self):
        token = LoginToken("session-token", expires_in=86400)
        token.user_info = UserInfo(
            username="session-user",
            display_name="Session User",
            time_zone="Asia/Shanghai",
            tenant_id="system",
        )
        token.user_info.provider_type = ProviderType.BK
        request = mock.MagicMock()
        request.session = {"user_token": token.dump_json()}

        restored = UniversalAuthBackend().get_token_from_session(request)

        assert restored is not None
        assert restored.login_token == token.login_token
        assert restored.expires_at == token.expires_at
        assert restored.issued_at == token.issued_at
        assert restored.user_info == token.user_info

    @override_settings(BKAUTH_BACKEND_TYPE="bk_token")
    def test_get_token_from_session_with_invalid_payload(self):
        request = mock.MagicMock()
        request.session = {"user_token": "not-json"}

        assert UniversalAuthBackend().get_token_from_session(request) is None

    @override_settings(BKAUTH_BACKEND_TYPE="bk_token")
    def test_get_token_from_session_with_legacy_pickled_payload(self):
        token = LoginToken("session-token", expires_in=86400)
        request = mock.MagicMock()
        request.session = {"user_token": pickle.dumps(token).decode("latin1")}

        assert UniversalAuthBackend().get_token_from_session(request) is None

    @pytest.mark.asyncio
    @override_settings(BKAUTH_BACKEND_TYPE="bk_token")
    async def test_async_get_token_from_session(self):
        token = LoginToken("session-token", expires_in=86400)
        token.user_info = UserInfo(username="session-user", display_name="Session User")
        token.user_info.provider_type = ProviderType.BK
        request = mock.MagicMock()
        request.session.aget = mock.AsyncMock(return_value=token.dump_json())

        restored = await UniversalAuthBackend().async_get_token_from_session(request)

        assert restored is not None
        assert restored.login_token == token.login_token
        request.session.aget.assert_awaited_once_with("user_token")

    @pytest.mark.asyncio
    @override_settings(BKAUTH_BACKEND_TYPE="bk_token")
    async def test_aget_user_restores_user_from_session(self):
        token = LoginToken("session-token", expires_in=86400)
        token.user_info = UserInfo(username="session-user", display_name="Session User")
        token.user_info.provider_type = ProviderType.BK

        backend = UniversalAuthBackend()
        backend.request = mock.MagicMock()
        backend.request.session.aget = mock.AsyncMock(return_value=token.dump_json())

        user = await backend.aget_user("any-user-id")

        assert user is not None
        assert user.username == "session-user"

    @pytest.mark.asyncio
    @override_settings(BKAUTH_BACKEND_TYPE="bk_token")
    async def test_aget_user_without_request(self):
        """未经 monkey patch 注入 request 时，无法从 session 还原用户"""
        assert await UniversalAuthBackend().aget_user("any-user-id") is None


# NOTE: 必须用 transaction=True。异步 ORM 通过 asgiref 的线程池执行，用的是另一条数据库连接，
# 不受普通 `db` fixture 的 atomic 块约束，写入的数据会真正提交并污染后续用例。
@pytest.mark.django_db(transaction=True)
class TestDjangoAuthUserCompatibleBackend:
    @pytest.fixture
    def backend(self, mocker):
        backend = DjangoAuthUserCompatibleBackend()
        mocker.patch.object(
            backend.request_backend,
            "async_request_user_account",
            new=mocker.AsyncMock(
                return_value=UserAccount(bk_username="django-async-user", display_name="Django Async User")
            ),
        )
        return backend

    @pytest.mark.asyncio
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_token")
    async def test_async_authenticate_uses_async_orm(self, backend, mocker):
        user = await backend.aauthenticate(request=mocker.MagicMock(), auth_credentials={"bk_token": "token"})

        assert user is not None
        assert user.username == "django-async-user"
        assert user.display_name == "Django Async User"
        assert user.is_authenticated

    @pytest.mark.asyncio
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_token")
    async def test_async_authenticate_calls_async_configure_user_on_creation(self, backend, mocker):
        configure_user = mocker.patch.object(
            backend, "async_configure_user", new=mocker.AsyncMock(side_effect=lambda db_user, bk_user: db_user)
        )

        await backend.aauthenticate(request=mocker.MagicMock(), auth_credentials={"bk_token": "token"})

        configure_user.assert_awaited_once()
        assert configure_user.await_args.kwargs["db_user"].username == "django-async-user"

    @pytest.mark.asyncio
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_token")
    async def test_async_connect_returns_none_when_user_absent(self, backend, mocker):
        mocker.patch.object(backend, "create_unknown_user", False)

        assert await backend.aauthenticate(request=mocker.MagicMock(), auth_credentials={"bk_token": "token"}) is None

    @pytest.mark.asyncio
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_token")
    async def test_async_connect_finds_existing_user(self, backend, mocker):
        mocker.patch.object(backend, "create_unknown_user", False)
        await get_user_model()._default_manager.acreate(username="django-async-user")

        user = await backend.aauthenticate(request=mocker.MagicMock(), auth_credentials={"bk_token": "token"})

        assert user is not None
        assert user.username == "django-async-user"
        # 兼容属性应当被写回到 Django 用户对象上
        assert user.display_name == "Django Async User"
        assert user.token is not None

    @pytest.mark.asyncio
    @override_settings(BKAUTH_ENABLE_MULTI_TENANT_MODE=False, BKAUTH_BACKEND_TYPE="bk_token")
    async def test_aget_user_connects_to_django_user(self, backend, mocker):
        token = LoginToken("session-token", expires_in=86400)
        token.user_info = UserInfo(username="django-async-user", display_name="Django Async User")
        token.user_info.provider_type = ProviderType.BK
        backend.request = mocker.MagicMock()
        backend.request.session.aget = mocker.AsyncMock(return_value=token.dump_json())

        user = await backend.aget_user("any-user-id")

        assert user is not None
        assert isinstance(user, get_user_model())
        assert user.username == "django-async-user"


class TestAPIGatewayAuthBackend:
    @pytest.fixture
    def backend(self):
        return APIGatewayAuthBackend()

    @pytest.mark.asyncio
    @override_settings(AUTHENTICATION_BACKENDS=["bkpaas_auth.backends.APIGatewayAuthBackend"])
    async def test_django_async_authenticate(self, mocker):
        user = await auth.aauthenticate(
            request=mocker.MagicMock(),
            gateway_name="test",
            bk_username="async-admin",
            verified=True,
        )

        assert user is not None
        assert user.is_authenticated
        assert user.username == "async-admin"
        assert user.backend == "bkpaas_auth.backends.APIGatewayAuthBackend"

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
