# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from typing import Optional
from unittest.mock import Mock

import pytest
from apigw_manager.apigw.providers import PublicKeyProvider
from apigw_manager.drf.authentication import ApiGatewayJWTAuthentication


class MockEmptyProvider(PublicKeyProvider):
    def provide(self, gateway_name: str, jwt_issuer: Optional[str] = None) -> Optional[str]:
        return None


class MockJwtProvider(PublicKeyProvider):
    def provide(self, gateway_name: str, jwt_issuer: Optional[str] = None) -> Optional[str]:
        jwt = Mock()
        jwt.payload = {
            "app": {"app_code": "mock_app", "verified": True},
            "user": {"username": "mock_user"},
        }
        jwt.gateway_name = "mock_gateway"

        return jwt


@pytest.fixture()
def mock_request(mocker):
    return mocker.MagicMock()


class TestApiGatewayJWTAuthentication:
    def test_authenticate_header(self):
        authentication = ApiGatewayJWTAuthentication()
        header = authentication.authenticate_header(Mock())

        assert header == "HTTP_X_BKAPI_JWT"

    def test_make_app(self):
        authentication = ApiGatewayJWTAuthentication()
        app = authentication.make_app(bk_app_code="my_app", verified=True)

        assert app.bk_app_code == "my_app"
        assert app.verified

    @pytest.fixture(autouse=True)
    def _patch_authenticate(self, mocker):
        self.authenticate_function = mocker.patch("django.contrib.auth.authenticate")

    def test_get_user(self):
        self.authenticate_function.return_value = "my_user"
        user = ApiGatewayJWTAuthentication().get_user(Mock())
        assert user == "my_user"

    def test_authenticate_invalid_provider(self):
        authentication = ApiGatewayJWTAuthentication()
        authentication.provider = MockEmptyProvider("mock")

        assert authentication.authenticate(Mock()) is None

    def test_authenticate(self, mock_request):
        self.authenticate_function.return_value = "my_user"

        authentication = ApiGatewayJWTAuthentication()
        authentication.provider = MockJwtProvider("mock")

        user, arg2 = authentication.authenticate(mock_request)
        assert arg2 is None
        assert user == "my_user"

        assert mock_request.app == authentication.make_app(bk_app_code="mock_app", verified=True)
