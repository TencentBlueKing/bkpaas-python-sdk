# -*- coding: utf-8 -*-
import pytest
from django.test.utils import override_settings

from bkpaas_auth.backends import APIGatewayAuthBackend, UniversalAuthBackend
from bkpaas_auth.core.constants import ProviderType


class TestBackends:
    def test_basic(self):
        backend = UniversalAuthBackend()
        backend.get_user('')


class TestAPIGatewayAuthBackend:
    @pytest.fixture
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
            api_name="test",
            bk_username="admin",
            verified=False,
        )

        assert user.is_anonymous
        assert not user.is_authenticated
        assert user.username == "admin"

    def test_authenticate_verified(self, mocker, backend):
        user = backend.authenticate(
            request=mocker.MagicMock(),
            api_name="test",
            bk_username="admin",
            verified=True,
        )

        assert not user.is_anonymous
        assert user.is_authenticated
        assert user.username == "admin"
