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
import requests

from bkapi_client_core import utils


@pytest.fixture
def fake_request():
    return requests.Request("GET", "https://example.com/get").prepare()


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


def test_to_curl(fake_request):
    request = None
    result = utils.to_curl(request)
    assert result == ""

    fake_request.prepare_headers({"foo": "bar"})
    result = utils.to_curl(fake_request)
    assert result == "curl -X GET -H 'foo: bar' https://example.com/get"


class TestSensitiveCleaner:
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                {
                    "secret": "bar",
                    "foo1": {
                        "secret": "baz",
                        "foo2": {
                            "secret": "ba2",
                        },
                    },
                    "foo3": [{"secret": "s3"}],
                    "foo4": [1, 2],
                },
                {
                    "secret": "***",
                    "foo1": {
                        "secret": "***",
                        "foo2": {
                            "secret": "***",
                        },
                    },
                    "foo3": [{"secret": "***"}],
                    "foo4": [1, 2],
                },
            )
        ],
    )
    def test_clean(self, data, expected):
        sensitive_cleaner = utils._SensitiveCleaner(["secret"])
        result = sensitive_cleaner.clean(data)
        assert result == expected


class TestWrappedRequest:
    @pytest.mark.parametrize(
        "headers, expected",
        [
            (
                {},
                {},
            ),
            (
                {"x-bkapi-authorization": '{"bk_app_code": "foo", "bk_app_secret": "bar"}'},
                {"X-Bkapi-Authorization": '{"bk_app_code": "foo", "bk_app_secret": "***"}'},
            ),
            (
                {"x-bkapi-authorization": '{"bk_app_code": "foo", "bk_app_secret": "bar", "bk_token": ""}'},
                {"X-Bkapi-Authorization": '{"bk_app_code": "foo", "bk_app_secret": "***", "bk_token": ""}'},
            ),
        ],
    )
    def test_get_headers_without_sensitive(self, fake_request, headers, expected):
        fake_request.prepare_headers(headers)
        wrapped_request = utils._WrappedRequest(fake_request)
        assert wrapped_request.headers == expected


class TestCurlRequest:
    def test_str(self, fake_request):
        result = utils.CurlRequest(fake_request).to_curl()
        assert result == "curl -X GET https://example.com/get"

        fake_request.prepare_url("https://example.com/get", {"foo": "bar"})
        fake_request.prepare_headers({"x-token": "test", "x-bkapi-authorization": '{"bk_app_secret": "bar"}'})
        result = utils.CurlRequest(fake_request).to_curl()
        assert result == (
            "curl -X GET -H 'X-Bkapi-Authorization: {\"bk_app_secret\": \"***\"}' "
            "-H 'x-token: test' 'https://example.com/get?foo=bar'"
        )
