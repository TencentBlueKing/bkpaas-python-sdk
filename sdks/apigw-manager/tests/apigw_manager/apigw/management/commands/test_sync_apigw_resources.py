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
def resource_signature_manager(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def command(mocker, manager, resource_signature_manager):
    command = Command()
    command.manager_class = mocker.MagicMock(return_value=manager)
    command.ResourceSignatureManager = mocker.MagicMock(return_value=resource_signature_manager)

    return command


def test_do(mocker, configuration, command, manager, resource_signature_manager):
    result = {
        "added": [],
        "deleted": [{"id": 1}, {"id": 2}],
        "updated": [{"id": 3}],
    }
    manager.sync_resources_config.return_value = result
    definition = {}

    command.do(manager, definition, configuration, delete=True)

    manager.sync_resources_config.assert_called_once_with(
        content=definition,
        delete=True,
    )
    resource_signature_manager.update_signature.assert_called_once_with(configuration.gateway_name, mocker.ANY)
    resource_signature_manager.mark_dirty.assert_called_once_with(configuration.gateway_name)


@pytest.mark.parametrize(
    ("added", "deleted", "dirty"),
    [
        (True, True, True),
        (True, False, True),
        (False, True, True),
        (False, False, False),
    ],
)
def test_update_signature(mocker, command, configuration, resource_signature_manager, added, deleted, dirty):
    command.update_signature(configuration.gateway_name, {}, added, deleted)
    resource_signature_manager.update_signature(configuration.gateway_name, mocker.ANY)

    if dirty:
        resource_signature_manager.mark_dirty.assert_called_once_with(configuration.gateway_name)
    else:
        resource_signature_manager.mark_clean.assert_not_called()
