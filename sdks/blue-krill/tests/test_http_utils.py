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
import json

import pytest
import requests
from requests.auth import HTTPBasicAuth

from blue_krill.http_utils import to_safe_curl
from tests.utils import assert_redacted

SECRET = "secret-value"


def prepare(**kwargs) -> requests.PreparedRequest:
    return requests.Request(**{"method": "POST", "url": "http://example.com/foo?a=1", **kwargs}).prepare()


class TestToSafeCurl:
    @pytest.mark.parametrize(
        "header",
        [
            "Authorization",
            "authorization",
            "Proxy-Authorization",
            "Cookie",
            "X-Bkapi-Authorization",
            "X-Api-Key",
            "X-Token",
            "X-Bk-App-Secret",
        ],
    )
    def test_mask_sensitive_headers(self, header):
        req = prepare(headers={header: SECRET, "X-Foo": "bar"})
        assert_redacted(
            to_safe_curl(req), secrets=[SECRET], expected=[f"{header}: ******", "X-Foo: bar", "http://example.com/foo"]
        )

    def test_keep_normal_headers(self):
        req = prepare(headers={"X-Bk-Tenant-Id": "tenant", "X-BKREPO-OVERWRITE": "True"})
        cmd = to_safe_curl(req)
        assert "X-Bk-Tenant-Id: tenant" in cmd
        assert "X-BKREPO-OVERWRITE: True" in cmd

    @pytest.mark.parametrize(
        "credentials",
        [
            {"bk_app_code": "app", "bk_app_secret": SECRET, "bk_token": SECRET},
            {"access_token": SECRET},
        ],
    )
    def test_bkapi_authorization_with_file_body(self, credentials):
        headers = {"X-Bkapi-Authorization": json.dumps(credentials), "X-Api-Key": SECRET}
        req = prepare(method="PUT", headers=headers, data=io.BytesIO(b"file"))
        assert_redacted(
            to_safe_curl(req), secrets=[SECRET], expected=["X-Bkapi-Authorization: ******", "X-Api-Key: ******"]
        )
        assert req.headers["X-Bkapi-Authorization"] == json.dumps(credentials)
        assert req.headers["X-Api-Key"] == SECRET

    def test_basic_auth(self):
        req = prepare(auth=HTTPBasicAuth("user", SECRET))
        assert_redacted(to_safe_curl(req), secrets=[req.headers["Authorization"]], expected=["Authorization: ******"])

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"json": {"pwd": SECRET}},
            {"data": {"pwd": SECRET}},
            {"data": SECRET.encode()},
            {"data": io.BytesIO(SECRET.encode())},
        ],
    )
    def test_body_omitted(self, kwargs):
        assert_redacted(to_safe_curl(prepare(**kwargs)), secrets=[SECRET], expected=["curl -X POST"])

    @pytest.mark.parametrize(
        "url",
        [
            f"http://admin:{SECRET}@example.com/foo",
            f"http://example.com/foo?token={SECRET}",
            f"http://admin:{SECRET}@example.com/foo?token={SECRET}",
        ],
    )
    def test_url_credentials(self, url):
        assert_redacted(to_safe_curl(prepare(url=url)), secrets=[SECRET], expected=["http://example.com/foo"])

    def test_original_request_unchanged(self):
        req = prepare(headers={"Authorization": SECRET}, json={"pwd": SECRET})
        to_safe_curl(req)
        assert req.headers["Authorization"] == SECRET
        assert req.body == f'{{"pwd": "{SECRET}"}}'.encode()

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("http://example.com/", "GET http://example.com/"),
            (f"http://admin:{SECRET}@example.com/foo?token={SECRET}", "GET http://example.com/foo"),
        ],
    )
    def test_fallback(self, url, expected):
        """When the curl command can not be generated, only the method and the redacted url are returned"""

        class BrokenRequest:
            method = "GET"

            def copy(self):
                raise RuntimeError("broken")

        request = BrokenRequest()
        request.url = url
        assert to_safe_curl(request) == expected  # type: ignore[arg-type]
