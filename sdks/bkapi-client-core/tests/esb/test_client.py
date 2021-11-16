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

from bkapi_client_core.esb.client import ESBClient


class TestESBClient:
    @pytest.mark.parametrize(
        "use_test_env, expected",
        [
            (True, {"X-Use-Test-Env": "true"}),
            (False, {}),
        ],
    )
    def test_set_use_test_env(self, use_test_env, expected):
        client = ESBClient()
        client.session.headers = {}

        client.set_use_test_env(use_test_env)
        assert client.session.headers == expected

    @pytest.mark.parametrize(
        "language, expected",
        [
            ("en", {"Blueking-Language": "en"}),
            ("", {}),
            (None, {}),
        ],
    )
    def test_set_language(self, language, expected):
        client = ESBClient()
        client.session.headers = {}

        client.set_language(language)
        assert client.session.headers == expected

    @pytest.mark.parametrize(
        "bk_api_ver, expected",
        [
            ("v2", {"bk_api_ver": "/v2"}),
            ("", {"bk_api_ver": ""}),
        ],
    )
    def test_set_bk_api_ver(self, bk_api_ver, expected):
        client = ESBClient()

        client.set_bk_api_ver(bk_api_ver)
        assert client.session.path_params == expected

    @pytest.mark.parametrize(
        "headers, key, value, expected",
        [
            ({}, "x-color", "red", {"x-color": "red"}),
            ({}, "x-color", "", {"x-color": ""}),
            ({"x-color": "red"}, "x-color", "green", {"x-color": "green"}),
        ],
    )
    def test_set_header(self, headers, key, value, expected):
        client = ESBClient()
        client.session.headers = headers

        client._set_header(key, value)
        assert client.session.headers == expected

    @pytest.mark.parametrize(
        "headers, key, expected",
        [
            ({"x-color": "red"}, "x-token", {"x-color": "red"}),
            ({"x-color": "red"}, "x-color", {}),
            ({}, "x-color", {}),
        ],
    )
    def test_delete_header(self, headers, key, expected):
        client = ESBClient()
        client.session.headers = headers

        client._delete_header(key)
        assert client.session.headers == expected
