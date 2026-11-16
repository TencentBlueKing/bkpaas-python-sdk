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

from apigw_manager.core.configuration import Configuration
from apigw_manager.core.handler import Handler


class TestHandlerSSLVerify:
    @pytest.mark.parametrize(
        ("env_value", "expected_verify"),
        [
            (None, True),
            ("true", True),
            ("True", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            (" false ", False),
            ("", True),
            ("invalid", True),
            ("0", True),
        ],
    )
    def test_ssl_verify_request(self, monkeypatch, mocker, env_value, expected_verify):
        if env_value is None:
            monkeypatch.delenv("BK_APIGW_MANAGER_ENABLE_SSL_VERIFY", raising=False)
        else:
            monkeypatch.setenv("BK_APIGW_MANAGER_ENABLE_SSL_VERIFY", env_value)
        config = Configuration(
            host="https://bkapi.example.com/api/bk-apigateway/prod",
            stage="",
            gateway_name="test-gateway",
        )
        response = mocker.MagicMock(status_code=200, headers={}, history=[], raw=None, is_redirect=False)
        response.json.return_value = {"data": {"public_key": "test-key"}}
        send = mocker.patch("requests.adapters.HTTPAdapter.send", return_value=response)
        handler = Handler(config)

        result = handler._call_v2(handler.client.api.v2_sync_get_gateway_public_key_new)

        assert result == {"data": {"public_key": "test-key"}}
        send.assert_called_once()
        assert send.call_args.kwargs["verify"] is expected_verify

    def test_ssl_verify_is_scoped_to_client(self, monkeypatch):
        config = Configuration()
        monkeypatch.setenv("BK_APIGW_MANAGER_ENABLE_SSL_VERIFY", "false")
        disabled_handler = Handler(config)
        monkeypatch.delenv("BK_APIGW_MANAGER_ENABLE_SSL_VERIFY")
        default_handler = Handler(config)

        assert disabled_handler.client.session.verify is False
        assert default_handler.client.session.verify is True
