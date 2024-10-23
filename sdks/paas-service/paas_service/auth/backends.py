# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions and
limitations under the License.

We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""
import logging
import time
from typing import Dict, Tuple

import jwt
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIRequest
from jwt.exceptions import DecodeError
from paas_service.models import ServiceInstance

logger = logging.getLogger(__name__)


class AuthFailedError(Exception):
    """Raised when one authenticator fails"""


class InstanceAuthFailed(Exception):
    pass


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

    def __init__(self):
        try:
            self.jwt_clients = settings.PAAS_SERVICE_JWT_CLIENTS
        except AttributeError:
            raise ImproperlyConfigured("PAAS_SERVICE_JWT_CLIENTS is not configured")

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
        raise ValueError('token is not a valid JWT token')

    @staticmethod
    def _validate_payload(client: Dict, payload: Dict) -> bool:
        """Validates given JWT payload, a valid payload must contain at least 2 fields:
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


class InstanceAuthBackend:
    TOKEN_KEY = 'token'

    def __init__(self):
        self.authenticators = [JWTClientAuthenticator()]

    def get_token(self, request: WSGIRequest):
        return request.GET.get(self.TOKEN_KEY, None)

    def invoke(self, request: WSGIRequest) -> ServiceInstance:
        """Invoke current backend

        :raises: InstanceAuthFailed
        """
        token = self.get_token(request)
        if not token:
            raise InstanceAuthFailed('token parameter is missing')

        for auth in self.authenticators:
            try:
                result = auth.authenticate(token)
                break
            except AuthFailedError:
                continue
        else:
            raise InstanceAuthFailed('token is invalid, can not be authenticated')

        instance_id = result.extra_payload.get('service_instance_id')
        if not instance_id:
            logger.warning('service_instance_id field is missing in token payload')
            raise InstanceAuthFailed('no service_instance_id field')

        try:
            instance = ServiceInstance.objects.get(pk=str(instance_id))
        except ServiceInstance.DoesNotExist:
            logger.warning(f'can not find a instance via id: {instance_id}')
            raise InstanceAuthFailed('service_instance_id is invalid')

        # Update session
        request.session['authorized_instances'] = {
            str(instance.uuid): True,
            **request.session.get('authorized_instances', {}),
        }
        return instance


def sign_instance_token(client_name: str, instance_uuid: str) -> str:
    """A quick access to sign a JWT token which is related to instance"""
    return _sign_token(client_name=client_name, additional_payload={"service_instance_id": instance_uuid})


def sign_role_aware_token(client_name: str, role_name: str) -> str:
    """A quick access to sign a role-aware JWT token"""
    return _sign_token(client_name=client_name, additional_payload={"role": role_name})


def _sign_token(client_name: str, additional_payload: Dict) -> str:
    """Sign a new JWT token using given client's credentials, this token can be used
    for an InstanceAuthBackend's authentication process.

    :returns: a JWT token which will expires after 3600 seconds
    :raises: ValueError if given client name is not valid
    """
    for client_data in settings.PAAS_SERVICE_JWT_CLIENTS:
        if client_name == client_data['iss']:
            payload = {'iss': client_name, 'expires_at': int(time.time()) + 3600}
            payload.update(additional_payload)
            return jwt.encode(payload, key=client_data['key'], algorithm=client_data['algorithm'])
    else:
        raise ValueError(f'client name {client_name} is invalid')
