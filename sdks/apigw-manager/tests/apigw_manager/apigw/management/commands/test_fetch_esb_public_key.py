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

from apigw_manager.apigw.management.commands.fetch_esb_public_key import Command


@pytest.fixture()
def manager(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def public_key_manager(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def command(mocker, manager, public_key_manager):
    mock_fun = mocker.patch("apigw_manager.apigw.helper.make_default_public_key_manager")
    mock_fun.return_value = public_key_manager

    command = Command()
    command.manager_class = mocker.MagicMock(return_value=manager)

    return command


def test_handle_no_save(command, manager, public_key_manager):
    command.handle(gateway_name="foo", print_=True, no_save=True)
    manager.public_key.assert_called()
    public_key_manager.set.assert_not_called()


def test_handle(command, manager, public_key_manager):
    command.handle(gateway_name="foo", print_=True, no_save=False)
    manager.public_key.assert_called()
    public_key_manager.set.assert_called()
