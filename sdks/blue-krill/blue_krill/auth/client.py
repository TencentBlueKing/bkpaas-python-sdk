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
from typing import Dict, Optional, Tuple

import jwt
from django.http import HttpRequest
from jwt.exceptions import DecodeError

from .jwt import DEFAULT_ALGORITHM
from .utils import get_paas_service_jwt_clients, validate_jwt_token

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
        for key in ('iss', 'key'):
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
                algorithm = client.get('algorithm', DEFAULT_ALGORITHM)
                payload = jwt.decode(token, client['key'], algorithms=[algorithm])
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


class VerifiedClientMiddleware:
    """when current request has a valid signed JWT token in headers, middleware will set two
    property on `request` object:

    - request.client: verified client object
    - request.extra_payload: extra payload from JWT token, usually includes current username etc.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def get_token(request) -> Optional[str]:
        """Get token from request, return None if no token can be found"""
        auth_header_val = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION')
        if not auth_header_val:
            return None

        try:
            _, token = auth_header_val.split(None, 1)
        except ValueError:
            logger.warning('Invalid authorization header value')
            return None
        return token

    def __call__(self, request):
        token = self.get_token(request)
        request.client = None
        request.extra_payload = None
        # Only proceed when token format is valid JWT format
        if token and validate_jwt_token(token):
            try:
                ret = JWTClientAuthenticator(get_paas_service_jwt_clients()).authenticate(token=token)
                request.client = ret.client
                request.extra_payload = ret.extra_payload
            except AuthFailedError as e:
                logger.info('Unable to create an authenticated client using token: %s, reason: %s', token, e)

        response = self.get_response(request)
        return response


def check_client_role(request: HttpRequest, role: str) -> bool:
    """Check if request contains a verified client and it's role matches given value"""
    client = getattr(request, 'client', None)
    if not (client and client.is_verified()):
        return False
    return request.client.role == role
