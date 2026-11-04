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

import logging
import time
from unittest.mock import MagicMock

import jwt
import pytest
from jwt.utils import base64url_encode
import requests
import requests_mock as requests_mock_mod
from django.utils.crypto import get_random_string

from blue_krill.auth.client import VerifiedClientMiddleware
from blue_krill.auth.jwt import ClientJWTAuth, JWTAuthConf


class TestClientJWTAuth:
    @pytest.mark.parametrize(("prefix", "expected_prefix"), [(None, "Bearer "), ("Basic", "Basic ")])
    def test_prefix(self, requests_mock, prefix, expected_prefix):
        conf = JWTAuthConf(iss="foo", key="bar", algorithm="HS256")
        if prefix:
            auth = ClientJWTAuth(conf, prefix=prefix)
        else:
            auth = ClientJWTAuth(conf)

        requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, text="resp")
        resp = requests.get("mock://", auth=auth)

        auth_header = resp.request.headers["Authorization"]
        assert auth_header != ""
        assert auth_header.startswith(expected_prefix)

    def test_extra_payload(self, requests_mock):
        key, algorithm = "bar", "HS256"
        conf = JWTAuthConf(iss="foo", key=key, algorithm=algorithm)
        auth = ClientJWTAuth(conf)

        requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, text="resp")
        resp = requests.get("mock://", auth=auth)
        auth_header = resp.request.headers["Authorization"]
        assert auth_header != ""

        # Parse token, check extra payload
        token = auth_header.split()[1]
        payload = jwt.decode(token, key, algorithms=[algorithm])
        assert payload["role"] == "default"


_JWT_CLIENT = {
    "iss": "foo",
    "key": get_random_string(length=12),
    "algorithm": "HS256",
    "role": "default",
}


@pytest.fixture(autouse=True)
def _setup_settings(settings):
    settings.PAAS_SERVICE_JWT_CLIENTS = [_JWT_CLIENT]


class TestVerifiedClientMiddleware:
    @pytest.mark.parametrize(
        ("key", "request_client_verified"),
        [
            (_JWT_CLIENT["key"], True),
            ("another_random_key", False),
        ],
    )
    def test_jwt_using_different_key(self, key, request_client_verified, rf):
        # Prepare JWT token string
        payload = {"iss": _JWT_CLIENT["iss"], "expires_at": time.time() + 3600, "role": "foo_role"}
        token = jwt.encode(payload, key=key, algorithm=_JWT_CLIENT["algorithm"])

        # Trigger middleware
        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
        VerifiedClientMiddleware(MagicMock())(request)

        if request_client_verified:
            assert request.client
            assert request.client.is_verified()
        else:
            assert request.client is None

    def test_not_jwt_token(self, rf):
        request = rf.get("/", HTTP_AUTHORIZATION="Bearer not-a-jwt-token")
        VerifiedClientMiddleware(MagicMock())(request)
        assert request.client is None


class TestTokenNotLogged:
    def test_client_jwt_auth(self, requests_mock, caplog):
        caplog.set_level(logging.DEBUG)
        auth = ClientJWTAuth(JWTAuthConf(iss="foo", key="bar", algorithm="HS256"))

        requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, text="resp")
        resp = requests.get("mock://", auth=auth)

        token = resp.request.headers["Authorization"].split()[1]
        assert token not in caplog.text
        assert token.rsplit(".", 1)[-1] not in caplog.text
        # The log should still be helpful for troubleshooting
        assert "iss='foo', expires_at=" in caplog.text
        assert f"signature=***{token[-6:]}" in caplog.text

    def test_client_and_middleware_logs_correlated(self, requests_mock, rf, caplog):
        """The token can be correlated by the masked signature in logs of both sides"""
        caplog.set_level(logging.DEBUG)
        # Sign the token using a key which is different from the server side
        auth = ClientJWTAuth(JWTAuthConf(iss=_JWT_CLIENT["iss"], key="another_random_key", algorithm="HS256"))
        requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, text="resp")
        header_value = requests.get("mock://", auth=auth).request.headers["Authorization"]

        request = rf.get("/", HTTP_AUTHORIZATION=header_value)
        VerifiedClientMiddleware(MagicMock())(request)

        assert request.client is None
        client_logs = [r.getMessage() for r in caplog.records if r.name == "blue_krill.auth.jwt"]
        server_logs = [r.getMessage() for r in caplog.records if r.name == "blue_krill.auth.client"]
        description = client_logs[0].split("token(", 1)[1]
        assert any(description in msg for msg in server_logs)

    def test_middleware_auth_failed(self, rf, caplog):
        caplog.set_level(logging.DEBUG)
        payload = {"iss": _JWT_CLIENT["iss"], "expires_at": time.time() + 3600, "role": "foo_role"}
        token = jwt.encode(payload, key="another_random_key", algorithm=_JWT_CLIENT["algorithm"])

        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
        VerifiedClientMiddleware(MagicMock())(request)

        assert request.client is None
        assert caplog.records, "no logs captured"
        assert token not in caplog.text
        # The log should still be helpful for troubleshooting
        assert f"iss='foo', expires_at='{payload['expires_at']}', signature=***{token[-6:]}" in caplog.text
        assert token.rsplit(".", 1)[-1] not in caplog.text

    @pytest.mark.parametrize(
        "payload",
        [
            # expired
            {"iss": _JWT_CLIENT["iss"], "expires_at": int(time.time()) - 3600},
            # issuer mismatched
            {"iss": "bar", "expires_at": int(time.time()) + 3600},
        ],
    )
    def test_middleware_invalid_claims(self, rf, caplog, payload):
        caplog.set_level(logging.INFO)
        token = jwt.encode(payload, key=_JWT_CLIENT["key"], algorithm=_JWT_CLIENT["algorithm"])

        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
        VerifiedClientMiddleware(MagicMock())(request)

        assert request.client is None
        assert token not in caplog.text
        assert f"iss='{payload['iss']}', expires_at='{payload['expires_at']}'" in caplog.text

    def test_middleware_undecodable_payload(self, rf, caplog):
        caplog.set_level(logging.INFO)
        # The payload is base64 encoded but not a valid JSON object
        signature = get_random_string(length=43)
        token = ".".join(
            [base64url_encode(b'{"alg":"HS256","typ":"JWT"}').decode(), base64url_encode(b"[1]").decode(), signature]
        )

        request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
        VerifiedClientMiddleware(MagicMock())(request)

        assert request.client is None
        assert signature not in caplog.text
        assert f"token(signature=***{signature[-6:]})" in caplog.text
