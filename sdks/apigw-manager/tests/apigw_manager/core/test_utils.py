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
from apigw_manager.core.utils import get_item, itemgetter
from pytest import fixture, raises


@fixture()
def test_data(faker):
    return {
        "a": {
            "color": faker.color(),
        },
        "b": {
            "color": faker.color(),
        },
    }


class TestGetItem:
    def test_usage(self, test_data):
        assert get_item(test_data, ["a", "color"]) == test_data["a"]["color"]

    def test_key_not_found(self, test_data):
        assert "nothing" not in test_data["a"]

        with raises(KeyError):
            get_item(test_data, ["a", "nothing"])


class TestItemGetter:
    def test_usage(self, test_data):
        getter = itemgetter("a", "color")
        assert getter(test_data) == test_data["a"]["color"]
