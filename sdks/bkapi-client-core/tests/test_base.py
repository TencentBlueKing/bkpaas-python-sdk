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

from bkapi_client_core.base import Operation, OperationGroup, OperationResource


class TestOperationResource:
    @pytest.fixture(autouse=True)
    def _setup(self, mocker):
        self.manager = mocker.MagicMock()
        self.resource = OperationResource()

    def test_on_init(self):
        assert self.resource.name == ""
        assert self.resource._manager is None

    def test_bind(self, faker):
        name = faker.pystr()

        self.resource.bind(name, self.manager)
        assert self.resource._manager is self.manager
        assert self.resource.name == name
        assert self.resource._manager is self.manager

    def test_str_with_manager(self):
        self.manager.__str__.return_value = "manager"
        self.resource.bind("testing", self.manager)

        assert self.resource._manager is not None
        assert str(self.resource) == "manager.testing"

    def test_str_without_manager(self):
        self.resource.name = "testing"

        assert self.resource._manager is None
        assert str(self.resource) == "testing"


class TestOperation:
    @pytest.fixture(autouse=True)
    def _setup(self, mocker):
        self.manager = mocker.MagicMock()
        self.operation = Operation()

    def test_call_without_bind(self):
        with pytest.raises(ValueError):  # noqa
            self.operation()

    def test_call_with_bind(self, faker):
        name = faker.pystr()
        client = self.manager.get_client.return_value
        result = client.parse_response.return_value

        self.operation.bind(name, self.manager)
        assert self.operation._manager is self.manager
        assert self.operation() is result

    @pytest.mark.parametrize(
        ("init_args", "call_args", "call_data", "excepted"),
        [
            (
                {"method": "POST", "path": "/"},
                {},
                {"x": 1},
                {"method": "POST", "path": "/", "data": {"x": 1}},
            ),
            (
                {"method": "GET", "path": "/"},
                {},
                {"x": 1},
                {"method": "GET", "path": "/", "data": {"x": 1}},
            ),
            (
                {"method": "GET", "path": "/"},
                {},
                None,
                {"method": "GET", "path": "/", "data": None},
            ),
            (
                {"method": "GET", "path": "/"},
                {"method": "POST", "path": "/test"},
                None,
                {"method": "POST", "path": "/test", "data": None},
            ),
        ],
    )
    def test_get_context(self, init_args, call_args, call_data, excepted, faker):
        operation = Operation(**init_args)
        operation.bind(faker.pystr(), self.manager)

        context = operation._get_context(data=call_data, **call_args)
        assert context == excepted


class TestOperationGroup:
    @pytest.fixture(autouse=True)
    def _setup(self, mocker, faker):
        self.manager = mocker.MagicMock()
        self.group = OperationGroup(name=faker.pystr(), manager=self.manager)

    def test_operation(self):
        operation = Operation()
        name = "test"

        self.group.register(name, operation)

        assert operation.name == name
        assert operation._manager == self.group
        assert getattr(self.group, name) is operation

    def test_operation_not_registered(self, faker):
        with pytest.raises(AttributeError):  # type: ignore
            getattr(self.group, faker.color())

    def test_operation_already_registered(self, faker):
        name = faker.color()

        self.group.register(name, Operation())

        with pytest.raises(ValueError):  # noqa
            self.group.register(name, Operation())

    def test_register_with_empty_name(self):
        with pytest.raises(ValueError):  # noqa
            self.group.register("", Operation())

    def test_handle_without_bind(self, mocker):
        group = OperationGroup()
        with pytest.raises(ValueError):  # noqa
            group.get_client()

    def test_handle_with_bind(self, mocker, faker):
        name = faker.pystr()
        manager = mocker.MagicMock()
        result = manager.get_client.return_value

        group = OperationGroup()
        group.bind(name, manager)
        assert group._manager is manager
        assert group.get_client() is result

    def test_registered_operation(self):
        operation = Operation()
        self.group.register("test", operation)

        assert self.group.test is operation

    def test_non_registered_operation(self):
        with pytest.raises(AttributeError):
            _ = self.group.test
