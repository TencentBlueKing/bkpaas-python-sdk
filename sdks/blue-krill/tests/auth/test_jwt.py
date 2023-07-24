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
import time
from unittest.mock import MagicMock

import jwt
import pytest
import requests
import requests_mock as requests_mock_mod
import six
from django.utils.crypto import get_random_string

from blue_krill.auth.client import VerifiedClientMiddleware
from blue_krill.auth.jwt import ClientJWTAuth, JWTAuthConf


class TestClientJWTAuth:
    @pytest.mark.parametrize('prefix,expected_prefix', [(None, 'Bearer '), ('Basic', 'Basic ')])
    def test_prefix(self, requests_mock, prefix, expected_prefix):
        conf = JWTAuthConf(iss='foo', key='bar', algorithm='HS256')
        if prefix:
            auth = ClientJWTAuth(conf, prefix=prefix)
        else:
            auth = ClientJWTAuth(conf)

        requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, text='resp')
        resp = requests.get('mock://', auth=auth)

        auth_header = resp.request.headers['Authorization']
        assert auth_header != ''
        assert auth_header.startswith(expected_prefix)

    def test_extra_payload(self, requests_mock):
        key, algorithm = 'bar', 'HS256'
        conf = JWTAuthConf(iss='foo', key=key, algorithm=algorithm)
        auth = ClientJWTAuth(conf)

        requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, text='resp')
        resp = requests.get('mock://', auth=auth)
        auth_header = resp.request.headers['Authorization']
        assert auth_header != ''

        # Parse token, check extra payload
        token = auth_header.split()[1]
        payload = jwt.decode(token, key, algorithms=[algorithm])
        assert payload['role'] == 'default'


_JWT_CLIENT = {
    'iss': 'foo',
    'key': get_random_string(length=12),
    'algorithm': 'HS256',
    'role': 'default',
}


@pytest.fixture(autouse=True)
def _setup_settings(settings):
    settings.PAAS_SERVICE_JWT_CLIENTS = [_JWT_CLIENT]


class TestVerifiedClientMiddleware:
    @pytest.mark.parametrize(
        'key,request_client_verified',
        [
            (_JWT_CLIENT['key'], True),
            ('another_random_key', False),
        ],
    )
    def test_jwt_using_different_key(self, key, request_client_verified, rf):
        # Prepare JWT token string
        payload = {'iss': _JWT_CLIENT['iss'], 'expires_at': time.time() + 3600, 'role': 'foo_role'}
        token = six.ensure_str(jwt.encode(payload, key=key, algorithm=_JWT_CLIENT['algorithm']))

        # Trigger middleware
        request = rf.get('/', HTTP_AUTHORIZATION=f'Bearer {token}')
        VerifiedClientMiddleware(MagicMock())(request)

        if request_client_verified:
            assert request.client
            assert request.client.is_verified()
        else:
            assert request.client is None

    def test_not_jwt_token(self, rf):
        request = rf.get('/', HTTP_AUTHORIZATION='Bearer not-a-jwt-token')
        VerifiedClientMiddleware(MagicMock())(request)
        assert request.client is None
