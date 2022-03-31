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

from apigw_manager.apigw.management.commands.sync_apigw_resources import Command


@pytest.fixture()
def manager(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def resource_sync_manager(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def command(mocker, manager, resource_sync_manager):
    command = Command()
    command.manager_class = mocker.MagicMock(return_value=manager)
    command.ResourceSyncManager = mocker.MagicMock(return_value=resource_sync_manager)

    return command


def test_do(mocker, configuration, command, manager, resource_sync_manager):
    result = {
        "added": [],
        "deleted": [{"id": 1}, {"id": 2}],
        "updated": [{"id": 3}],
    }
    manager.sync_resources_config.return_value = result
    definition = mocker.MagicMock()

    command.do(manager, definition, configuration, delete=True)

    manager.sync_resources_config.assert_called_once_with(
        content=definition,
        delete=True,
    )
    resource_sync_manager.set.assert_called_once_with(
        configuration.api_name,
        len(result["added"]),
        len(result["deleted"]),
        len(result["updated"]),
    )
