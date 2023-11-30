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

from apigw_manager.apigw import command


class TestApiCommand:
    @pytest.fixture(autouse=True)
    def _setup_command(self):
        self.command = command.ApiCommand()

    def test_get_configuration(self, configuration):
        result = self.command.get_configuration()

        assert configuration.gateway_name == result.gateway_name
        assert configuration.host == result.host

    def test_get_configuration_with_args(self, faker):
        gateway_name = faker.color
        host = faker.url()
        result = self.command.get_configuration(gateway_name=gateway_name, host=host)

        assert gateway_name == result.gateway_name
        assert host.startswith(result.host)


class TestDefinitionCommand:
    @pytest.fixture(autouse=True)
    def _setup_command(self):
        self.command = command.DefinitionCommand()

    def test_get_context(self):
        context = self.command.get_context(["a:1", "b:2"])

        assert "settings" in context
        assert "environ" in context
        assert context["data"]["a"] == 1
        assert context["data"]["b"] == 2
