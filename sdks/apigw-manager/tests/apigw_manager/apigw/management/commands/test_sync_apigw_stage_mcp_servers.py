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

from apigw_manager.apigw.management.commands.sync_apigw_stage_mcp_servers import Command


@pytest.fixture()
def command():
    return Command()


def test_do_uses_v2_result_data_directly(mock_manager, command, capsys):
    stage_definition = {
        "name": "prod",
        "mcp_servers": [
            {
                "name": "demo",
                "description": "demo",
                "resource_names": ["get_user"],
                "status": "active",
            }
        ],
    }
    mock_manager.sync_stage_mcp_servers.return_value = [
        {"id": 1, "name": "gateway-prod-demo", "action": "create"},
        {"id": 2, "name": "gateway-prod-demo-2", "action": "update"},
    ]

    command.do(mock_manager, [stage_definition])

    mock_manager.sync_stage_mcp_servers.assert_called_once_with(**stage_definition)
    captured = capsys.readouterr()
    assert (
        "API gateway stage mcp servers synchronization completed [ id:1,name:gateway-prod-demo,action:create ]"
        in captured.out
    )
    assert (
        "API gateway stage mcp servers synchronization completed [ id:2,name:gateway-prod-demo-2,action:update ]"
        in captured.out
    )


def test_do_ignores_empty_v2_result(mock_manager, command, capsys):
    stage_definition = {
        "name": "prod",
        "mcp_servers": [],
    }
    mock_manager.sync_stage_mcp_servers.return_value = []

    command.do(mock_manager, [stage_definition])

    mock_manager.sync_stage_mcp_servers.assert_called_once_with(**stage_definition)
    captured = capsys.readouterr()
    assert captured.out == ""
