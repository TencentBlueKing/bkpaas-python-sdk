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
from bkapi_client_core.property import BindProperty


class TestBindProperty:
    def test_bind_with_name(self, mocker):
        attr = mocker.MagicMock()
        mock_cls = mocker.MagicMock(return_value=attr)

        class Manager(object):
            attr = BindProperty(mock_cls)

        manager = Manager()
        # call twice
        assert isinstance(manager.attr, mocker.MagicMock)
        assert isinstance(manager.attr, mocker.MagicMock)

        mock_cls.assert_called_once()
        attr.bind.assert_called_once_with(mocker.ANY, manager)

    def test_without_name(self, mocker):
        attr = mocker.MagicMock()
        mock_cls = mocker.MagicMock(return_value=attr)

        class NoNameBindProperty(BindProperty):
            def __set_name__(self, instance, name):
                pass

        class Manager(object):
            attr = NoNameBindProperty(mock_cls)

        manager = Manager()
        # call twice
        assert isinstance(manager.attr, mocker.MagicMock)
        assert isinstance(manager.attr, mocker.MagicMock)

        mock_cls.assert_called_once()
        attr.bind.assert_called_once_with("", manager)

    def test_lazy_init(self, mocker):
        attr = mocker.MagicMock()
        mock_cls = mocker.MagicMock(return_value=attr)

        class Manager(object):
            attr = BindProperty(mock_cls, 1, x=2)

        assert Manager.attr is mock_cls
        mock_cls.assert_not_called()

        manager = Manager()
        mock_cls.assert_not_called()

        # visit the attr
        manager.attr
        manager.attr

        mock_cls.assert_called_once_with(1, x=2)
        attr.bind.assert_called_once_with(mocker.ANY, manager)

    def test_multi_instances(self, mocker):
        class Manager(object):
            attr = BindProperty(mocker.MagicMock)

        manager1 = Manager()
        manager2 = Manager()

        assert manager1.attr is not manager2.attr
