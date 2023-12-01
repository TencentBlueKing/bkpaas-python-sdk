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

from apigw_manager.apigw.helper import (
    ContextManager,
    Definition,
    PublicKeyManager,
    ReleaseVersionManager,
    ResourceSignatureManager,
)
from apigw_manager.apigw.models import Context


class TestDefinition:
    def test_load(self):
        definition = Definition.load(
            "a: {{a}}",
            {
                "a": 1,
            },
        )

        assert definition.loaded["a"] == 1

    @pytest.mark.parametrize(
        ("namespace", "level"),
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
            """
        level: 1
        a:
            level: 2
            b:
                level: 3
                c:
                    level: 4
        """
        )

        result = definition.get(namespace)
        assert result["level"] == level


class TestContextManager:
    @pytest.fixture(autouse=True)
    def _setup_manager(self, faker):
        self.manager = ContextManager()
        self.manager.scope = faker.pystr()

    def test_get_value_not_found(self, faker):
        assert self.manager.get_value(faker.pystr()) is None

    def test_get_value(self, faker):
        key = faker.pystr()
        context = Context.objects.create(scope=self.manager.scope, key=key, value=faker.pystr())

        assert self.manager.get_value(key) == context.value

    def test_get_values(self, faker):
        key1 = faker.pystr()
        key2 = faker.pystr()

        context1 = Context.objects.create(scope=self.manager.scope, key=key1, value=faker.pystr())
        context2 = Context.objects.create(scope=self.manager.scope, key=key2, value=faker.pystr())

        assert self.manager.get_values([]) == {}
        assert self.manager.get_values([key1]) == {key1: context1.value}
        assert self.manager.get_values([key1, key2]) == {key1: context1.value, key2: context2.value}

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
    def _setup_manager(self):
        self.manager = PublicKeyManager()

    def test_get_not_found(self, fake_gateway_name):
        assert self.manager.get(fake_gateway_name) is None

    def test_get(self, fake_gateway_name, faker):
        context = Context.objects.create(
            scope=self.manager.scope,
            key=fake_gateway_name,
            value=faker.pystr(),
        )
        assert self.manager.get(fake_gateway_name) == context.value

    def test_best_matched(self, faker):
        jwt_issuer = faker.pystr()
        gateway_name = faker.pystr()

        context1 = Context.objects.create(
            key="%s:%s" % (jwt_issuer, gateway_name), scope=self.manager.scope, value=faker.pystr()
        )
        context2 = Context.objects.create(key=gateway_name, scope=self.manager.scope, value=faker.pystr())

        public_key = self.manager.get_best_matched(gateway_name)
        assert public_key == context2.value

        public_key = self.manager.get_best_matched(gateway_name, jwt_issuer)
        assert public_key == context1.value

        public_key = self.manager.get_best_matched(gateway_name, "not-exist")
        assert public_key == context2.value

        public_key = self.manager.get_best_matched("not-exist")
        assert public_key is None

        public_key = self.manager.get_best_matched("not-exist", jwt_issuer)
        assert public_key is None

    def test_set(self, fake_gateway_name, faker):
        self.manager.set(fake_gateway_name, faker.pystr())
        self.manager.set(fake_gateway_name, faker.pystr())
        self.manager.set(fake_gateway_name, faker.pystr(), faker.pystr())

    def test_get_key(self):
        assert self.manager._get_key("foo") == "foo"
        assert self.manager._get_key("foo", "bar") == "bar:foo"

    def test_current(self, fake_gateway_name, faker):
        context = Context.objects.create(
            scope=self.manager.scope,
            key=fake_gateway_name,
            value=faker.pystr(),
        )

        assert self.manager.current() == context.value


class TestReleaseVersionManager:
    @pytest.fixture(autouse=True)
    def _setup_manager(self):
        self.manager = ReleaseVersionManager()

    def test_increase(self, faker):
        gateway_name = faker.pystr()

        for excepted in ["v1", "v2", "v3"]:
            assert self.manager.increase(gateway_name) == excepted


class TestResourceSignatureManager:
    @pytest.fixture(autouse=True)
    def _setup_manager(self):
        self.manager = ResourceSignatureManager()

    def test_get_not_found(self, faker):
        assert self.manager.get(faker.pystr()) == {}

    def test_get(self, faker):
        gateway_name = faker.pystr()
        self.manager.set(gateway_name, False, "signature")
        assert self.manager.get(gateway_name) == {
            "is_dirty": False,
            "signature": "signature",
        }

    def test_get_signature_default(self, faker):
        assert self.manager.get_signature(faker.pystr()) == ""

    def test_get_signature(self, faker):
        gateway_name = faker.pystr()
        self.manager.set(gateway_name, False, "signature")
        assert self.manager.get_signature(gateway_name) == "signature"

    @pytest.mark.parametrize(
        "is_dirty",
        [True, False],
    )
    def test_is_dirty(self, faker, is_dirty):
        gateway_name = faker.pystr()
        self.manager.set(gateway_name, is_dirty, "signature")
        assert self.manager.is_dirty(gateway_name) == is_dirty

    @pytest.mark.parametrize(
        "is_dirty",
        [True, False],
    )
    def test_is_dirty_default(self, faker, is_dirty):
        gateway_name = faker.pystr()
        assert self.manager.is_dirty(gateway_name, is_dirty) == is_dirty

    def test_mark_dirty(self, faker):
        gateway_name = faker.pystr()
        self.manager.mark_dirty(gateway_name)
        assert self.manager.get(gateway_name) == {
            "is_dirty": True,
            "signature": "",
        }

    def test_reset_dirty(self, faker):
        gateway_name = faker.pystr()
        self.manager.reset_dirty(gateway_name)
        assert self.manager.get(gateway_name) == {
            "is_dirty": False,
            "signature": "",
        }

    def test_update_signature_at_first_time(self, faker):
        gateway_name = faker.pystr()
        self.manager.update_signature(gateway_name, "signature")
        assert self.manager.get(gateway_name) == {
            "is_dirty": True,
            "signature": "signature",
        }

    @pytest.mark.parametrize(
        "is_dirty",
        [True, False],
    )
    def test_update_signature_not_change(self, faker, is_dirty):
        gateway_name = faker.pystr()
        self.manager.set(gateway_name, is_dirty, "signature")

        self.manager.update_signature(gateway_name, "signature")
        assert self.manager.get(gateway_name) == {
            "is_dirty": is_dirty,
            "signature": "signature",
        }

    def test_update_signature_changed(self, faker):
        gateway_name = faker.pystr()
        self.manager.set(gateway_name, False, "")

        self.manager.update_signature(gateway_name, "signature")
        assert self.manager.get(gateway_name) == {
            "is_dirty": True,
            "signature": "signature",
        }
