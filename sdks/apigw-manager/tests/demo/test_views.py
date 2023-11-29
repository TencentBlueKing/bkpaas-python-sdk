"""
 TencentBlueKing is pleased to support the open source community by
 making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 You may obtain a copy of the License at http://opensource.org/licenses/MIT
 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 specific language governing permissions and limitations under the License.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.fixture()
def jwt_headers(public_key_context, jwt_encoded):
    return {"HTTP_X_BKAPI_JWT": jwt_encoded}


@pytest.fixture()
def csrf_client(client: Client):
    client.handler.enforce_csrf_checks = True
    return client


@pytest.fixture(autouse=True)
def user_object(jwt_user, faker):
    user_model = get_user_model()

    return user_model.objects.create_user(username=jwt_user["username"], password=faker.color_name())


def test_jwt_info(csrf_client: Client, jwt_headers: dict, jwt_decoded: dict, fake_gateway_name):
    response = csrf_client.post("/test/jwt", **jwt_headers)
    result = response.json()

    assert result["api_name"] == fake_gateway_name
    assert result["payload"] == jwt_decoded


def test_jwt_app(csrf_client: Client, jwt_headers: dict, jwt_app: dict):
    response = csrf_client.post("/test/app", **jwt_headers)
    result = response.json()

    assert result["bk_app_code"] == jwt_app["app_code"]
    assert result["verified"] == jwt_app["verified"]


def test_jwt_user(csrf_client: Client, jwt_headers: dict, user_object):
    response = csrf_client.post("/test/user", **jwt_headers)
    result = response.json()

    assert result["username"] == user_object.username
    assert not result["is_anonymous"]
