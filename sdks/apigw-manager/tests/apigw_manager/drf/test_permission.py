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
from apigw_manager.drf.permission import ApiGatewayPermission


class Request:
    pass


class App:
    verified = False


class User:
    is_authenticated = False


@pytest.fixture()
def empty_request(mocker):
    return Request()


@pytest.fixture()
def jwt_request(mocker):
    # request = mocker.MagicMock()
    request = Request()
    request.jwt = mocker.MagicMock()
    request.jwt.payload = {}
    return request


@pytest.fixture()
def exempt_view(mocker):
    view = mocker.MagicMock()
    view.FROM_APIGW_EXEMPT = True
    return view


@pytest.fixture()
def view(mocker):
    view = mocker.MagicMock()
    view.FROM_APIGW_EXEMPT = False
    return view


class TestApiGatewayPermission:
    def test_has_permission_exempt_view(self, empty_request, exempt_view):
        permission = ApiGatewayPermission()
        assert permission.has_permission(empty_request, exempt_view) is True

    def test_has_permission_missing_jwt(self, empty_request, view):
        permission = ApiGatewayPermission()
        assert permission.has_permission(empty_request, view) is False

    def test_has_permission_no_app(self, jwt_request, view):
        permission = ApiGatewayPermission()
        view.app_verified_required = True
        assert permission.has_permission(jwt_request, view) is False

    def test_has_permission_app_verified_false(self, jwt_request, view):
        permission = ApiGatewayPermission()
        view.app_verified_required = True
        jwt_request.app = App()
        jwt_request.app.verified = False
        assert permission.has_permission(jwt_request, view) is False

    def test_has_permission_no_user(self, jwt_request, view):
        permission = ApiGatewayPermission()
        view.app_verified_required = False
        view.user_verified_required = True
        assert permission.has_permission(jwt_request, view) is False

    def test_has_permission_user_not_authenticated(self, jwt_request, view):
        permission = ApiGatewayPermission()
        view.app_verified_required = False
        view.user_verified_required = True

        jwt_request.user = User()
        jwt_request.user.is_authenticated = False
        assert permission.has_permission(jwt_request, view) is False

    def test_pass(self, jwt_request, view):
        permission = ApiGatewayPermission()
        view.app_verified_required = True
        jwt_request.app = App()
        jwt_request.app.verified = True

        view.user_verified_required = True
        jwt_request.user = User()
        jwt_request.user.is_authenticated = True
        assert permission.has_permission(jwt_request, view) is True
