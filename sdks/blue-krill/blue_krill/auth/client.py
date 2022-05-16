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
import logging
import time
from typing import Dict, Tuple

import jwt
from django.http import HttpRequest
from jwt.exceptions import DecodeError

logger = logging.getLogger(__name__)


class AuthFailedError(Exception):
    """Raised when one authenticator fails"""


class Client:
    def __init__(self, name, auth_backend_type=None, role=None):
        self.name = name
        self.auth_backend_type = auth_backend_type
        self.role = role

    def __str__(self):
        return self.name

    def is_verified(self):
        return True

    @classmethod
    def from_jwt_settings(cls, data):
        for key in ('iss', 'algorithm', 'key'):
            if not data.get(key):
                raise ValueError(f'error: {key} is required')
        return cls(name=data['iss'], auth_backend_type='jwt')


class AuthResult:
    """result for authentication"""

    def __init__(self, client: Client, extra_payload: Dict):
        self.client = client
        self.extra_payload = extra_payload


class JWTClientAuthenticator:
    """Authenticator using JWT clients"""

    def __init__(self, jwt_clients):
        self.jwt_clients = jwt_clients

    def authenticate(self, token: str) -> AuthResult:
        """Authenticate a given token

        :raises: AuthFailedError
        """
        try:
            payload, client = self.parse(token)
        except ValueError as e:
            logger.warning(f'authentication failed, token is invalid: {e}')
            raise AuthFailedError('token is invalid')
        else:
            logger.info(f'successfully authenticated token issued by {client}')
            return AuthResult(client=client, extra_payload=payload)

    def parse(self, token: str) -> Tuple[Dict, Client]:
        """Parse given token

        :raises: ValueError when token is invalid
        """
        for client in self.jwt_clients:
            try:
                payload = jwt.decode(token, client['key'], algorithms=[client['algorithm']])
            except DecodeError:
                logger.debug(f'Unable to decode token using {client["iss"]}\'s secret')
                continue

            if not self._validate_payload(client, payload):
                logger.debug('payload validation failed')
                continue

            client_ins = Client.from_jwt_settings(client)
            client_ins.role = payload.get('role')
            return payload, client_ins
        raise ValueError('invalid JWT token')

    @staticmethod
    def _validate_payload(client: Dict, payload: Dict) -> bool:
        """Validates given JWT payload, a valid payload must contains at least 2 fields:
        'iss' and 'expires_at'.
        """
        expires_at = payload.get('expires_at')
        try:
            expires_at = int(expires_at)  # type: ignore
        except (TypeError, ValueError):
            logger.warning("token's expires_at is empty or invalid")
            return False
        if expires_at < time.time():
            logger.warning("token has already expired")
            return False

        iss = payload.get('iss')
        if not (iss and iss == client['iss']):
            logger.warning("issuer name in payload does not match client's config")
            return False
        return True


def check_client_role(request: HttpRequest, role: str) -> bool:
    """Check if request contains a verified client and it's role matches given value"""
    client = getattr(request, 'client', None)
    if not (client and client.is_verified()):
        return False
    return request.client.role == role
