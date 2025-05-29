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

import os

import pytest
from faker import Faker

from apigw_manager.core.exceptions import ApiResponseError
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

    def test_call_with_cache(self, handler: Handler, operation, operation_id, faker, mocker):
        result = faker.pydict()
        operation.return_value = result
        mock_get_from_cache = mocker.patch.object(Handler, "_get_from_cache", return_value=(False, None))
        mock_put_into_cache = mocker.patch.object(Handler, "_put_into_cache", return_value=None)

        gateway_name = faker.pystr()
        kwargs = {
            "gateway_name": gateway_name,
            "foo": "bar",
        }

        handler._call_with_cache(operation, **kwargs)

        cache_key = {
            "gateway_name": gateway_name,
            "kwargs": {"gateway_name": gateway_name, "foo": "bar"},
        }
        mock_get_from_cache.assert_called_once_with(operation_id, cache_key)
        mock_put_into_cache.assert_called_once_with(operation_id, cache_key, result)

    def test_call_connect_error(self, handler: Handler, operation):
        operation.side_effect = HTTPResponseError()
        with pytest.raises(ApiResponseError):
            handler._call(operation)

    def test_call_server_error(self, handler: Handler, operation, mocker):
        operation.side_effect = HTTPResponseError(response=mocker.MagicMock(status_code=500))
        with pytest.raises(ApiResponseError):
            handler._call(operation)

    def test_call_request_error(self, handler: Handler, operation, mocker):
        operation.side_effect = HTTPResponseError(
            response=mocker.MagicMock(
                status_code=400,
                json=mocker.MagicMock(return_value={"code": "400", "message": "request error"}),
            )
        )

        with pytest.raises(ApiResponseError):
            handler._call(operation)

    def test_call_request_error_with_no_json(self, handler: Handler, operation, mocker):
        operation.side_effect = HTTPResponseError(
            response=mocker.MagicMock(
                status_code=400,
                json=mocker.MagicMock(side_effect=ValueError()),
            )
        )

        with pytest.raises(ApiResponseError):
            handler._call(operation)

    def test_get_tenant_id_from_config(self, handler: Handler, mocker):
        handler.config.bk_app_tenant_id = "123"
        assert handler._get_tenant_id() == "123"

    def test_get_tenant_id_from_env(self, handler: Handler, mocker):
        mocker.patch.object(
            os.environ, "get", side_effect=lambda key: "123" if key == "BKPAAS_APP_TENANT_ID" else None
        )
        assert handler._get_tenant_id() == "123"

    def test_get_tenant_id_from_env_default_system(self, handler: Handler, mocker):
        mocker.patch.object(os.environ, "get", side_effect=lambda key: "" if key == "BKPAAS_APP_TENANT_ID" else None)
        assert handler._get_tenant_id() == "system"
