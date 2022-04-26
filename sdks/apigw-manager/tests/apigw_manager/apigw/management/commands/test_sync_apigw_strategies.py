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

from apigw_manager.apigw.management.commands.sync_apigw_strategies import Command


@pytest.fixture()
def command():
    return Command()


def test_do(mock_manager, command, faker):
    scope_type = "stage"
    rate_limit_config = faker.pydict()
    error_status_code_200_config = faker.pydict()

    command.do(
        mock_manager,
        [
            {"type": "rate_limit", "config": rate_limit_config},
            {"type": "error_status_code_200", "config": error_status_code_200_config},
        ],
        scope_type,
    )

    mock_manager.sync_access_strategies.assert_any_call(
        name="rate_limit_stage",
        scopes=[],
        scope_type=scope_type,
        rate_limit=rate_limit_config,
        type="rate_limit",
    )
    mock_manager.sync_access_strategies.assert_any_call(
        name="error_status_code_200_stage",
        scopes=[],
        scope_type=scope_type,
        error_status_code_200=error_status_code_200_config,
        type="error_status_code_200",
    )
