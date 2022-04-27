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

from apigw_manager.apigw.management.commands.grant_apigw_permissions import Command


@pytest.fixture()
def command():
    return Command()


def test_do(mock_manager, command):
    command.do(
        mock_manager,
        [
            {"bk_app_code": "test1"},
            {"bk_app_code": "test2"},
        ],
    )

    mock_manager.grant_permission.assert_any_call(
        target_app_code="test1",
        grant_dimension="api",
    )
    mock_manager.grant_permission.assert_any_call(
        target_app_code="test2",
        grant_dimension="api",
    )
