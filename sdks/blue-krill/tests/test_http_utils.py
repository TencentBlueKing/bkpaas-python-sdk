# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import io

import pytest
import requests
from requests.auth import HTTPBasicAuth

from blue_krill.http_utils import to_safe_curl


def prepare(**kwargs) -> requests.PreparedRequest:
    return requests.Request(**{"method": "POST", "url": "http://example.com/foo?a=1", **kwargs}).prepare()


class TestToSafeCurl:
    @pytest.mark.parametrize("header", ["Authorization", "authorization", "Proxy-Authorization", "Cookie"])
    def test_mask_sensitive_headers(self, header):
        req = prepare(headers={header: "secret-value", "X-Foo": "bar"})
        cmd = to_safe_curl(req)
        assert "secret-value" not in cmd
        assert f"{header}: ******" in cmd
        assert "X-Foo: bar" in cmd
        assert "http://example.com/foo" in cmd

    def test_basic_auth(self):
        req = prepare(auth=HTTPBasicAuth("user", "secret-password"))
        assert req.headers["Authorization"] not in to_safe_curl(req)

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"json": {"pwd": "secret-value"}},
            {"data": {"pwd": "secret-value"}},
            {"data": b"secret-value"},
            {"data": io.BytesIO(b"secret-value")},
        ],
    )
    def test_body_omitted(self, kwargs):
        assert "secret-value" not in to_safe_curl(prepare(**kwargs))

    @pytest.mark.parametrize(
        "url",
        [
            "http://admin:secret-value@example.com/foo",
            "http://example.com/foo?token=secret-value",
            "http://admin:secret-value@example.com/foo?token=secret-value",
        ],
    )
    def test_url_credentials(self, url):
        cmd = to_safe_curl(prepare(url=url))
        assert "secret-value" not in cmd
        assert "http://example.com/foo" in cmd

    def test_original_request_unchanged(self):
        req = prepare(headers={"Authorization": "secret-value"}, json={"pwd": "secret-value"})
        to_safe_curl(req)
        assert req.headers["Authorization"] == "secret-value"
        assert req.body == b'{"pwd": "secret-value"}'

    def test_fallback(self):
        class BrokenRequest:
            method = "GET"
            url = "http://example.com/"

            def copy(self):
                raise RuntimeError("broken")

        assert to_safe_curl(BrokenRequest()) == "GET http://example.com/"  # type: ignore[arg-type]

    def test_fallback_url_credentials(self):
        class BrokenRequest:
            method = "GET"
            url = "http://admin:secret-value@example.com/foo?token=secret-value"

            def copy(self):
                raise RuntimeError("broken")

        assert to_safe_curl(BrokenRequest()) == "GET http://example.com/foo"  # type: ignore[arg-type]
