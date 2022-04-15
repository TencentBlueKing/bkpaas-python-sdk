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
from apigw_manager.apigw.decorators import apigw_require


@apigw_require
def view_func(request):
    return "success"


@pytest.fixture()
def mock_invalid_request(rf):
    return rf.get("/")


@pytest.fixture()
def mock_valid_request(rf):
    req = rf.get("/")
    req.jwt = "jwt_token"
    setattr(req, "jwt", "jwt_token")
    return req


@pytest.fixture()
def mock_exempt_request(settings, rf):
    settings.BK_APIGW_REQUIRE_EXEMPT = True
    return rf.get("/")


class TestAPIGWRequire:
    def test_reject_request(self, mock_invalid_request):
        response = view_func(mock_invalid_request)
        assert response.status_code == 403

    def test_success(self, mock_valid_request):
        response = view_func(mock_valid_request)
        assert response == "success"

    def test_exempt(self, mock_exempt_request):
        response = view_func(mock_invalid_request)
        assert response == "success"
