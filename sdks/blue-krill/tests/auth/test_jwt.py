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
import requests
import requests_mock as requests_mock_mod
from django.utils.crypto import get_random_string
from jwt.utils import base64url_encode

from blue_krill.auth.client import VerifiedClientMiddleware
from blue_krill.auth.jwt import ClientJWTAuth, JWTAuthConf
from tests.utils import assert_redacted


@pytest.fixture(autouse=True)
def _capture_all_logs(caplog):
    caplog.set_level(logging.DEBUG)


def send_request(requests_mock, auth) -> str:
    """Send a request with the given auth, return the value of the "Authorization" header"""
    requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, text="resp")
    return requests.get("mock://", auth=auth).request.headers["Authorization"]


def assert_token_not_logged(caplog, token: str, expected: str):
    """The token, including its signature, must not be logged, but the description of it should be"""
    signature = token.rsplit(".", 1)[-1]
    assert_redacted(caplog.text, secrets=[token, signature], expected=[expected, f"signature=***{signature[-6:]}"])


class TestClientJWTAuth:
    @pytest.mark.parametrize(("prefix", "expected_prefix"), [(None, "Bearer "), ("Basic", "Basic ")])
    def test_prefix(self, requests_mock, caplog, prefix, expected_prefix):
        conf = JWTAuthConf(iss="foo", key="bar", algorithm="HS256")
        if prefix:
            auth = ClientJWTAuth(conf, prefix=prefix)
        else:
            auth = ClientJWTAuth(conf)

        auth_header = send_request(requests_mock, auth)
        assert auth_header.startswith(expected_prefix)
        token = auth_header[len(expected_prefix) :]
        assert token != ""
        assert_token_not_logged(caplog, token, "jwt authorization header injected, token(iss='foo', expires_at=")

    def test_extra_payload(self, requests_mock):
        key, algorithm = "bar", "HS256"
        conf = JWTAuthConf(iss="foo", key=key, algorithm=algorithm)
        auth = ClientJWTAuth(conf)

        auth_header = send_request(requests_mock, auth)
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


def call_middleware(rf, token: str):
    request = rf.get("/", HTTP_AUTHORIZATION=f"Bearer {token}")
    VerifiedClientMiddleware(MagicMock())(request)
    return request


class TestVerifiedClientMiddleware:
    @pytest.mark.parametrize(
        ("key", "request_client_verified"),
        [
            (_JWT_CLIENT["key"], True),
            ("another_random_key", False),
        ],
    )
    def test_jwt_using_different_key(self, key, request_client_verified, rf, caplog):
        # Prepare JWT token string
        payload = {"iss": _JWT_CLIENT["iss"], "expires_at": time.time() + 3600, "role": "foo_role"}
        token = jwt.encode(payload, key=key, algorithm=_JWT_CLIENT["algorithm"])

        # Trigger middleware
        request = call_middleware(rf, token)

        if request_client_verified:
            assert request.client
            assert request.client.is_verified()
        else:
            assert request.client is None
            assert_token_not_logged(caplog, token, f"token(iss='foo', expires_at='{payload['expires_at']}'")

    @pytest.mark.parametrize(
        "payload",
        [
            # expired
            {"iss": _JWT_CLIENT["iss"], "expires_at": int(time.time()) - 3600},
            # issuer mismatched
            {"iss": "bar", "expires_at": int(time.time()) + 3600},
        ],
    )
    def test_invalid_claims(self, rf, caplog, payload):
        token = jwt.encode(payload, key=_JWT_CLIENT["key"], algorithm=_JWT_CLIENT["algorithm"])
        request = call_middleware(rf, token)

        assert request.client is None
        assert_token_not_logged(caplog, token, f"token(iss='{payload['iss']}', expires_at='{payload['expires_at']}'")

    def test_not_jwt_token(self, rf):
        request = call_middleware(rf, "not-a-jwt-token")
        assert request.client is None

    def test_undecodable_payload(self, rf, caplog):
        # The payload is base64 encoded but not a valid JSON object
        header, payload = base64url_encode(b'{"alg":"HS256","typ":"JWT"}'), base64url_encode(b"[1]")
        token = ".".join([header.decode(), payload.decode(), get_random_string(length=43)])
        request = call_middleware(rf, token)

        assert request.client is None
        assert_token_not_logged(caplog, token, "token(signature=")


def test_client_and_middleware_logs_correlated(requests_mock, rf, caplog):
    """The token can be correlated by the masked signature in logs of both sides"""
    # Sign the token using a key which is different from the server side
    auth = ClientJWTAuth(JWTAuthConf(iss=_JWT_CLIENT["iss"], key="another_random_key", algorithm="HS256"))
    token = send_request(requests_mock, auth).split()[1]
    request = call_middleware(rf, token)

    assert request.client is None
    client_logs = [r.getMessage() for r in caplog.records if r.name == "blue_krill.auth.jwt"]
    server_logs = [r.getMessage() for r in caplog.records if r.name == "blue_krill.auth.client"]
    description = client_logs[0].split("token(", 1)[1]
    assert any(description in msg for msg in server_logs)
