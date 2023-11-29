# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.cache import caches
from django.core.cache.backends.dummy import DummyCache

from apigw_manager.apigw import authentication, providers
from apigw_manager.apigw.providers import CachePublicKeyProvider, DefaultJWTProvider, SettingsPublicKeyProvider


@pytest.fixture()
def mock_response(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def mock_request(rf):
    return rf.get("/")


@pytest.fixture()
def request_user(mock_request, mocker):
    mock_request.user = mocker.MagicMock()
    return mock_request.user


@pytest.fixture()
def django_jwt_cache_name():
    return "test-jwt"


@pytest.fixture()
def django_jwt_cache(settings, django_jwt_cache_name, mocker):
    settings.APIGW_JWT_PUBLIC_KEY_CACHE_MINUTES = 1
    settings.APIGW_JWT_PUBLIC_KEY_CACHE_VERSION = "0"
    settings.APIGW_JWT_PUBLIC_KEY_CACHE_NAME = django_jwt_cache_name

    cache = mocker.MagicMock()
    caches[django_jwt_cache_name] = cache

    try:
        yield cache
    finally:
        del caches[django_jwt_cache_name]


@pytest.fixture()
def apigw_request(jwt_encoded, mock_request):
    mock_request.META["HTTP_X_BKAPI_JWT"] = jwt_encoded
    return mock_request


@pytest.fixture()
def jwt_request(fake_gateway_name, jwt_decoded, mock_request):
    mock_request.jwt = providers.DecodedJWT(
        api_name=fake_gateway_name,
        payload=jwt_decoded,
    )

    return mock_request


@pytest.fixture()
def invalid_apigw_request(mock_request):
    mock_request.META[
        "HTTP_X_BKAPI_JWT"
    ] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoibHljIn0.iHy-g0R-q3sVnO16gTHV0FAIViEuKMGCtNLNVYSJX5c"

    return mock_request


class TestApiGatewayJWTMiddleware:
    @pytest.fixture(autouse=True)
    def _setup_middleware(self, mock_response, fake_gateway_name):
        self.middleware = authentication.ApiGatewayJWTMiddleware(mock_response)

    def test_default_config(self, fake_gateway_name, jwt_algorithm):
        assert isinstance(self.middleware.provider, DefaultJWTProvider)
        assert self.middleware.provider.default_api_name == fake_gateway_name
        assert self.middleware.provider.algorithm == jwt_algorithm
        assert self.middleware.provider.allow_invalid_jwt_token is False
        assert isinstance(self.middleware.provider.public_key_provider, SettingsPublicKeyProvider)

    def test_call_without_jwt(self, mock_response, mock_request):
        assert self.middleware.JWT_KEY_NAME not in mock_request.META

        self.middleware(mock_request)
        mock_response.assert_called_with(mock_request)

        assert not hasattr(mock_request, "jwt")

    def test_call_without_public_key(self, settings, apigw_request, mock_response):
        assert not hasattr(settings, "APIGW_PUBLIC_KEY")

        self.middleware(apigw_request)
        mock_response.assert_called_with(apigw_request)

        assert not hasattr(mock_request, "jwt")

    def test_call(self, settings, public_key, apigw_request, mock_response, fake_gateway_name):
        assert self.middleware.JWT_KEY_NAME in apigw_request.META

        settings.APIGW_PUBLIC_KEY = public_key

        self.middleware(apigw_request)
        mock_response.assert_called_with(apigw_request)

        assert apigw_request.jwt.api_name == fake_gateway_name
        assert apigw_request._dont_enforce_csrf_checks

    def test_jwt_invalid(self, settings, public_key, invalid_apigw_request, mock_response):
        middleware = authentication.ApiGatewayJWTMiddleware(mock_response)
        settings.APIGW_PUBLIC_KEY = public_key

        with pytest.raises(providers.JWTTokenInvalid):
            middleware(invalid_apigw_request)

    def test_allow_jwt_invalid(self, settings, public_key, invalid_apigw_request, mock_response):
        settings.APIGW_ALLOW_INVALID_JWT_TOKEN = True
        settings.APIGW_PUBLIC_KEY = public_key

        middleware = authentication.ApiGatewayJWTMiddleware(mock_response)
        middleware(invalid_apigw_request)
        mock_response.assert_called_with(invalid_apigw_request)


class TestApiGatewayJWTGenericMiddleware:
    def test_init_with_settings(self, settings, mock_response, django_jwt_cache):
        middleware = authentication.ApiGatewayJWTGenericMiddleware(mock_response)

        assert isinstance(middleware.provider, DefaultJWTProvider)
        assert isinstance(middleware.provider.public_key_provider, CachePublicKeyProvider)
        assert (
            middleware.provider.public_key_provider.cache_expires == settings.APIGW_JWT_PUBLIC_KEY_CACHE_MINUTES * 60
        )
        assert middleware.provider.public_key_provider.cache_version == settings.APIGW_JWT_PUBLIC_KEY_CACHE_VERSION
        assert middleware.provider.public_key_provider.cache == django_jwt_cache

    def test_init_without_settings(self, mock_response):
        middleware = authentication.ApiGatewayJWTGenericMiddleware(mock_response)

        assert isinstance(middleware.provider, DefaultJWTProvider)
        assert isinstance(middleware.provider.public_key_provider, CachePublicKeyProvider)
        assert middleware.provider.public_key_provider.cache_expires == 0
        assert middleware.provider.public_key_provider.cache_version == 0
        assert isinstance(middleware.provider.public_key_provider.cache, DummyCache)


class TestApiGatewayJWTAppMiddleware:
    @pytest.fixture(autouse=True)
    def _setup_middleware(self, mock_response):
        self.middleware = authentication.ApiGatewayJWTAppMiddleware(mock_response)

    def test_make_app(self):
        app = self.middleware.make_app(bk_app_code="testing", verified=False)

        assert app.bk_app_code == "testing"
        assert app.verified is False

    def test_call_without_jwt(self, mock_request, mock_response):
        assert not hasattr(mock_request, "jwt")

        self.middleware(mock_request)

        assert not hasattr(mock_request, "app")
        mock_response.assert_called_with(mock_request)

    @pytest.mark.parametrize("field", ["app_code", "bk_app_code"])
    def test_call_with_jwt(self, jwt_request, mock_response, jwt_app, field):
        jwt_app = jwt_request.jwt.payload["app"]
        app_code = jwt_app.pop("app_code", None) or jwt_app.pop("bk_app_code", None)
        jwt_app[field] = app_code

        self.middleware(jwt_request)

        assert jwt_request.app.bk_app_code == app_code
        assert jwt_request.app.verified == jwt_app["verified"]
        mock_response.assert_called_with(jwt_request)


class TestApiGatewayJWTUserMiddleware:
    @pytest.fixture(autouse=True)
    def _setup_middleware(self, mock_response):
        self.middleware = authentication.ApiGatewayJWTUserMiddleware(mock_response)

    @pytest.fixture(autouse=True)
    def _patch_authenticate(self, mocker):
        self.authenticate_function = mocker.patch("django.contrib.auth.authenticate")

    @pytest.fixture(autouse=True)
    def _setup_user(self, mocker):
        self.user = mocker.MagicMock()

    def test_get_user(self, jwt_request):
        self.authenticate_function.return_value = self.user
        assert self.middleware.get_user(jwt_request) == self.user

    def test_get_user_not_found(self, jwt_request):
        self.authenticate_function.return_value = None
        assert self.middleware.get_user(jwt_request) is None

    def test_call_without_jwt(self, mock_request, mock_response):
        assert not hasattr(mock_request, "jwt")

        self.middleware(mock_request)

        assert not hasattr(mock_request, "user")
        mock_response.assert_called_with(mock_request)

    def test_call_with_authenticated_user(self, mock_request, mock_response, request_user):
        self.middleware(mock_request)

        assert mock_request.user == request_user
        mock_response.assert_called_with(mock_request)

    @pytest.mark.parametrize("field", ["username", "bk_username"])
    def test_call_with_jwt(self, jwt_request, mock_response, field):
        self.authenticate_function.return_value = self.user

        jwt_user = jwt_request.jwt.payload["user"]
        username = jwt_user.pop("username", None) or jwt_user.pop("bk_username", None)
        jwt_user[field] = username

        self.middleware(jwt_request)

        assert jwt_request.user == self.user
        mock_response.assert_called_with(jwt_request)


class TestUserModelBackend:
    @pytest.fixture(autouse=True)
    def _setup_backend(self, mocker):
        self.user_maker = mocker.MagicMock()
        self.backend = authentication.UserModelBackend()
        self.backend.user_maker = self.user_maker

    def test_authenticate_user(self, mock_request):
        user = self.backend.authenticate(mock_request, api_name="test", bk_username="admin", verified=True)
        assert not isinstance(user, AnonymousUser)
        self.user_maker.assert_called_with("admin")

    def test_authenticate_anonymou_user(self, mock_request):
        user = self.backend.authenticate(mock_request, api_name="test", bk_username="admin", verified=False)
        assert isinstance(user, AnonymousUser)
        self.user_maker.assert_not_called()
