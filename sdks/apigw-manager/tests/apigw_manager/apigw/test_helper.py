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

from apigw_manager.apigw.helper import ContextManager, Definition, PublicKeyManager, ReleaseVersionManager
from apigw_manager.apigw.models import Context


class TestDefinition:
    def test_load(self):
        definition = Definition.load(
            'a: {{a}}',
            {
                'a': 1,
            },
        )

        assert definition.loaded['a'] == 1

    @pytest.mark.parametrize(
        ["namespace", "level"],
        [
            (None, 1),
            ("", 1),
            ("a", 2),
            ("a.b", 3),
            ("a.b.c", 4),
        ],
    )
    def test_get(self, namespace, level):
        definition = Definition(
            '''
        level: 1
        a:
            level: 2
            b:
                level: 3
                c:
                    level: 4
        '''
        )

        result = definition.get(namespace)
        assert result["level"] == level


class TestContextManager:
    @pytest.fixture(autouse=True)
    def setup_manager(self, faker):
        self.manager = ContextManager()
        self.manager.scope = faker.pystr()

    def test_get_value_not_found(self, faker):
        assert self.manager.get_value(faker.pystr()) is None

    def test_get_value(self, faker):
        key = faker.pystr()
        context = Context.objects.create(scope=self.manager.scope, key=key, value=faker.pystr())

        assert self.manager.get_value(key) == context.value

    def test_set_value(self, faker):
        key = faker.pystr()
        value = faker.pystr()

        assert self.manager.set_value(key, value)

        context = Context.objects.get(scope=self.manager.scope, key=key)
        assert context.value == value

        assert not self.manager.set_value(key, value)

        context = Context.objects.get(pk=context.pk)
        assert context.value == value


class TestPublicKeyManager:
    @pytest.fixture(autouse=True)
    def setup_manager(self):
        self.manager = PublicKeyManager()

    def test_get_not_found(self, api_name):
        assert self.manager.get(api_name) is None

    def test_get(self, api_name, faker):
        context = Context.objects.create(
            scope=self.manager.scope,
            key=api_name,
            value=faker.pystr(),
        )
        assert self.manager.get(api_name) == context.value

    def test_set(self, api_name, faker):
        self.manager.set(api_name, faker.pystr())
        self.manager.set(api_name, faker.pystr())

    def test_current(self, api_name, faker):
        context = Context.objects.create(
            scope=self.manager.scope,
            key=api_name,
            value=faker.pystr(),
        )

        assert self.manager.current() == context.value


class TestReleaseVersionManager:
    @pytest.fixture(autouse=True)
    def setup_manager(self):
        self.manager = ReleaseVersionManager()

    def test_increase(self, faker):
        api_name = faker.pystr()

        for excepted in ["v1", "v2", "v3"]:
            assert self.manager.increase(api_name) == excepted
