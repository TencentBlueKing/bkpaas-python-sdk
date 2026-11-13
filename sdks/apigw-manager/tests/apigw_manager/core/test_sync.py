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
import yaml

from apigw_manager.core.sync import Synchronizer


@pytest.mark.parametrize("version", ["2.0", "3.0.3", "3.1.0"])
@pytest.mark.parametrize(
    "deprecation",
    [
        {},
        {"deprecated": True, "x-bk-apigateway-resource": {"deprecatedNote": "请使用 get_users_v2"}},
        {"deprecated": True, "x-bk-apigateway-resource": {"deprecatedNote": ""}},
        {"deprecated": False, "x-bk-apigateway-resource": {"deprecatedNote": ""}},
    ],
)
def test_sync_resources_preserves_deprecation(config, mocker, version, deprecation):
    operation = {
        "operationId": "get_users",
        "responses": {"200": {"description": "OK"}},
        **deprecation,
    }
    content = {
        "swagger" if version == "2.0" else "openapi": version,
        "info": {"title": "Users", "version": "1"},
        "paths": {"/users/": {"get": operation}},
    }
    synchronizer = Synchronizer(config)
    synchronizer.client = mocker.MagicMock()
    endpoint = synchronizer.client.api.v2_sync_resources
    endpoint.path = "/api/v2/sync/gateways/{gateway_name}/resources/"
    endpoint.return_value = {"data": {"added": [], "updated": [], "deleted": []}}

    assert synchronizer.sync_resources_config(content=content, delete=False) == endpoint.return_value["data"]
    assert yaml.safe_load(endpoint.call_args.kwargs["data"]["content"]) == content
