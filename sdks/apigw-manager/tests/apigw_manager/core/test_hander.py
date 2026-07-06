# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import pytest
from faker import Faker

from apigw_manager.core.exceptions import ApiResponseError, ApiResultError
from apigw_manager.core.handler import Handler
from bkapi_client_core.exceptions import HTTPResponseError


@pytest.fixture()
def handler(api_instance, config):
    return Handler(config)


@pytest.fixture()
def operation_id(faker: Faker):
    return faker.color_name()


@pytest.fixture()
def operation(mocker, operation_id):
    mock_operation = mocker.MagicMock()
    mock_operation.name = operation_id

    return mock_operation


@pytest.fixture()
def api_data(faker: Faker):
    return faker.pydict()


class TestHandler:
    def test_get_from_cache_not_set(self, handler: Handler, operation_id, api_data):
        assert handler.config.api_cache is None

        ok, result = handler._get_from_cache(operation_id, api_data)

        assert not ok
        assert result is None

    def test_get_from_cache_has_set(self, handler: Handler, api_cache, operation_id, api_data):
        assert handler.config.api_cache is not None
        api_cache.try_get.return_value = (True, {})

        ok, result = handler._get_from_cache(operation_id, api_data)

        assert ok
        assert result is not None

    def test_put_into_cache_not_set(self, handler: Handler, operation_id, api_data):
        assert handler.config.api_cache is None

        assert not handler._put_into_cache(operation_id, api_data, {})

    def test_put_into_cache_has_set(self, handler: Handler, api_cache, operation_id, api_data):
        assert handler.config.api_cache is not None

        assert handler._put_into_cache(operation_id, api_data, {})

    def test_call_v2_request_error_parse_error_body(self, handler: Handler, operation, mocker):
        operation.path = "/api/v2/sync/gateways/{gateway_name}/"
        operation.side_effect = HTTPResponseError(
            response=mocker.MagicMock(
                status_code=400,
                json=mocker.MagicMock(
                    return_value={
                        "error": {
                            "code": "AuthFailure",
                            "message": "The provided credentials could not be validated.",
                            "system": "bkiam",
                            "details": [
                                {
                                    "code": "SignatureFailure",
                                    "message": "",
                                    "module": "auth",
                                    "links": "",
                                    "doc": "",
                                }
                            ],
                            "data": {},
                        }
                    }
                ),
            )
        )

        with pytest.raises(ApiResultError) as err:
            handler._call_v2(operation)

        assert err.value.code == "AuthFailure"
        assert err.value.message == "The provided credentials could not be validated."

    def test_call_v2_request_error_with_no_json(self, handler: Handler, operation, mocker):
        operation.path = "/api/v2/sync/gateways/{gateway_name}/"
        operation.side_effect = HTTPResponseError(
            response=mocker.MagicMock(
                status_code=500,
                text="server error",
                json=mocker.MagicMock(side_effect=ValueError()),
            )
        )

        with pytest.raises(ApiResultError) as err:
            handler._call_v2(operation)

        assert err.value.code == 500
        assert err.value.message == "server error"

    def test_call_v2_connect_error(self, handler: Handler, operation):
        operation.path = "/api/v2/sync/gateways/{gateway_name}/"
        operation.side_effect = HTTPResponseError()

        with pytest.raises(ApiResponseError) as err:
            handler._call_v2(operation)

        assert not isinstance(err.value, ApiResultError)

    @pytest.mark.parametrize(
        "data",
        [
            {},
            [],
            {"id": 1, "name": "gateway"},
        ],
    )
    def test_parse_v2_result_returns_data_for_success_response(self, handler: Handler, data):
        result = {"data": data}

        assert handler._parse_v2_result(result) == data

    def test_get_tenant_id_from_config(self, handler: Handler, mocker):
        handler.config.bk_app_tenant_id = "123"
        assert handler._get_tenant_id() == "123"

    def test_get_tenant_id_from_env(self, handler: Handler, monkeypatch):
        monkeypatch.setenv("BKPAAS_APP_TENANT_ID", "123")
        assert handler._get_tenant_id() == "123"

    def test_get_tenant_id_from_env_default_system(self, handler: Handler, monkeypatch):
        monkeypatch.setenv("BKPAAS_APP_TENANT_ID", "")
        assert handler._get_tenant_id() == "system"
