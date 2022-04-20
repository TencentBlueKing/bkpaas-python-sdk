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
from bkapi_client_core import utils


@pytest.mark.parametrize(
    "base_url, path, expected",
    [
        (None, "/test/", "/test/"),
        ("", "/test/", "/test/"),
        ("http://demo.example.com/", "/test/", "http://demo.example.com/test/"),
        ("http://demo.example.com/test", "/red/", "http://demo.example.com/test/red/"),
        ("http://demo.example.com/test", "", "http://demo.example.com/test"),
    ],
)
def test_urljoin(base_url, path, expected):
    result = utils.urljoin(base_url, path)
    assert result == expected


@pytest.mark.parametrize(
    "curlify, request_, expected",
    [
        ({"to_curl.return_value": "curl http://example.com"}, None, ""),
        ({"to_curl.return_value": "curl http://example.com"}, {"a": "b"}, "curl http://example.com"),
    ],
)
def test_to_curl(mocker, curlify, request_, expected):
    mocker.patch.object(utils, "curlify", curlify and mocker.MagicMock(**curlify))
    result = utils.to_curl(request_ and mocker.MagicMock(**request_))
    assert result == expected
