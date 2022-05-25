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

import abc
import logging
from typing import Optional

import jwt
from django.http.request import HttpRequest
from django.conf import settings
from future.utils import raise_from

logger = logging.getLogger(__name__)


class JWTTokenInvalid(Exception):
    pass


class DecodedJWT:
    def __init__(self, api_name: str, payload: dict) -> None:
        self.api_name = api_name
        self.payload = payload


class JWTProvider(metaclass=abc.ABCMeta):
    def __init__(self, default_api_name: str, algorithm: str, allow_invalid_jwt_token: bool, **kwargs) -> None:
        self.default_api_name = default_api_name
        self.algorithm = algorithm
        self.allow_invalid_jwt_token = allow_invalid_jwt_token

    @abc.abstractclassmethod
    def provide(self, request: HttpRequest) -> Optional[DecodedJWT]:
        """
        provide should extract jwt from rquest and return a DecodedJWT
        and return None when process error
        """


class DefaultProvider(JWTProvider):
    def _decode_jwt(self, jwt_payload, public_key, algorithm):
        return jwt.decode(
            jwt_payload,
            public_key,
            algorithms=algorithm,
        )

    def _decode_jwt_header(self, jwt_payload):
        return jwt.get_unverified_header(jwt_payload)

    def _get_public_key(self, api_name, jwt_issuer=None):
        public_key = getattr(settings, "APIGW_PUBLIC_KEY", None)
        if not public_key:
            logger.warning(
                "No `APIGW_PUBLIC_KEY` can be found in settings, you should either configure it "
                "with a valid value or remove `APIGatewayLoginMiddleware` middleware entirely"
            )
        return public_key

    def provide(self, request: HttpRequest) -> DecodedJWT:
        jwt_token = request.META.get(self.JWT_KEY_NAME, "")
        if not jwt_token:
            return None

        try:
            jwt_header = self._decode_jwt_header(jwt_token)
            api_name = jwt_header.get("kid") or self.default_api_name
            public_key = self._get_public_key(api_name, jwt_header.get("iss"))
            if not public_key:
                logger.warning("no public key found")
                return None

            algorithm = jwt_header.get("alg") or self.algorithm
            decoded = self._decode_jwt(
                jwt_token,
                public_key,
                algorithm,
            )

            return DecodedJWT(api_name=api_name, payload=decoded)

        except jwt.PyJWTError as e:
            if not self.allow_invalid_jwt_token:
                raise_from(JWTTokenInvalid, e)

        return None
