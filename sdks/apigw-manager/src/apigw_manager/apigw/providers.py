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
import os
from typing import Optional

import jwt
from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.dummy import DummyCache
from django.http.request import HttpRequest
from future.utils import raise_from

from apigw_manager.apigw.helper import make_default_public_key_manager

logger = logging.getLogger(__name__)


class JWTTokenInvalid(Exception):
    pass


# public key provider


class PublicKeyProvider(metaclass=abc.ABCMeta):
    def __init__(self, default_gateway_name: str):
        self.default_gateway_name = default_gateway_name

    @abc.abstractmethod
    def provide(self, gateway_name: str, jwt_issuer: Optional[str] = None) -> Optional[str]:
        """
        provide should return public key base on gateway_name and jwt_issuer and
        return None when process error
        """


class SettingsPublicKeyProvider(PublicKeyProvider):
    def provide(self, gateway_name: str, jwt_issuer: Optional[str] = None) -> Optional[str]:
        """Return the public key specified by Settings"""
        public_key = getattr(settings, "APIGW_PUBLIC_KEY", None)
        if not public_key:
            logger.warning(
                "No `APIGW_PUBLIC_KEY` can be found in settings, you should either configure it "
                "with a valid value or remove `APIGatewayLoginMiddleware` middleware entirely"
            )
        return public_key


class CachePublicKeyProvider(SettingsPublicKeyProvider):
    """
    settings.APIGW_JWT_PUBLIC_KEY_CACHE_MINUTES is used to set the public key cache expires,
    if the value is 0, it does not need to cache.

    settings.APIGW_JWT_PUBLIC_KEY_CACHE_NAME is the name of the cache instance.

    settings.APIGW_JWT_PUBLIC_KEY_CACHE_VERSION is the current version of cache.
    """

    CACHE_MINUTES = 0
    CACHE_NAME = "default"
    CACHE_VERSION = 0

    def __init__(self, default_gateway_name: str):
        super().__init__(default_gateway_name)

        self.cache_expires = getattr(settings, "APIGW_JWT_PUBLIC_KEY_CACHE_MINUTES", self.CACHE_MINUTES) * 60
        self.cache_version = getattr(settings, "APIGW_JWT_PUBLIC_KEY_CACHE_VERSION", self.CACHE_VERSION)

        self.public_key_manager = make_default_public_key_manager()

        cache_name = getattr(settings, "APIGW_JWT_PUBLIC_KEY_CACHE_NAME", self.CACHE_NAME)

        # If the cache expires is 0, it does not need to cache
        if self.cache_expires:
            self.cache = caches[cache_name]
        else:
            self.cache = DummyCache(cache_name, params={})

    def provide(self, gateway_name: str, jwt_issuer: Optional[str] = None) -> Optional[str]:
        """Get the specified public key from Context model, if not specified, return the default value"""
        cache_key = "apigw:public_key:%s:%s" % (jwt_issuer or "", gateway_name)
        cached_value = self.cache.get(cache_key)
        if cached_value:
            return cached_value

        public_key = self.public_key_manager.get_best_matched(gateway_name, jwt_issuer)
        if not public_key:
            return super(CachePublicKeyProvider, self).provide(gateway_name, jwt_issuer)

        self.cache.set(cache_key, public_key, self.cache_expires, self.cache_version)
        return public_key


# jwt key provider


class DecodedJWT:
    def __init__(self, gateway_name: str, payload: dict) -> None:
        self.gateway_name = gateway_name
        self.payload = payload
        # api_name 保留为保持兼容，其于 gateway_name 一致
        self.api_name = gateway_name


class JWTProvider(metaclass=abc.ABCMeta):
    def __init__(
        self,
        jwt_key_name: str,
        default_gateway_name: str,
        algorithm: str,
        allow_invalid_jwt_token: bool,
        public_key_provider: PublicKeyProvider,
        **kwargs,
    ) -> None:
        self.jwt_key_name = jwt_key_name
        self.default_gateway_name = default_gateway_name
        self.algorithm = algorithm
        self.allow_invalid_jwt_token = allow_invalid_jwt_token
        self.public_key_provider = public_key_provider

    @abc.abstractmethod
    def provide(self, request: HttpRequest) -> Optional[DecodedJWT]:
        """
        provide should extract jwt from request and return a DecodedJWT
        and return None when process error
        """


class DefaultJWTProvider(JWTProvider):
    def _decode_jwt(self, jwt_payload, public_key, algorithm):
        return jwt.decode(
            jwt_payload,
            public_key,
            algorithms=[algorithm],
        )

    def _decode_jwt_header(self, jwt_payload):
        return jwt.get_unverified_header(jwt_payload)

    def provide(self, request: HttpRequest) -> Optional[DecodedJWT]:
        jwt_token = request.META.get(self.jwt_key_name, "")
        if not jwt_token:
            return None

        try:
            jwt_header = self._decode_jwt_header(jwt_token)
            gateway_name = jwt_header.get("kid") or self.default_gateway_name
            public_key = self.public_key_provider.provide(gateway_name, jwt_header.get("iss"))
            if not public_key:
                logger.warning("no public key found, gateway=%s, issuer=%s", gateway_name, jwt_header.get("iss"))
                return None

            algorithm = jwt_header.get("alg") or self.algorithm
            decoded = self._decode_jwt(jwt_token, public_key, algorithm)

            return DecodedJWT(gateway_name=gateway_name, payload=decoded)

        except jwt.PyJWTError as e:
            if not self.allow_invalid_jwt_token:
                raise_from(JWTTokenInvalid, e)

        return None


class DummyEnvPayloadJWTProvider(JWTProvider):
    def provide(self, request: HttpRequest) -> DecodedJWT:
        gateway_name = os.getenv("APIGW_MANAGER_DUMMY_GATEWAY_NAME", "") or os.getenv(
            "APIGW_MANAGER_DUMMY_API_NAME", ""
        )
        bk_app_code = os.getenv("APIGW_MANAGER_DUMMY_PAYLOAD_APP_CODE", "")
        bk_username = os.getenv("APIGW_MANAGER_DUMMY_PAYLOAD_USERNAME", "")
        return DecodedJWT(
            gateway_name=gateway_name,
            payload={
                "app": {"app_code": bk_app_code, "verified": bool(bk_app_code)},
                "user": {"username": bk_username, "verified": bool(bk_username)},
            },
        )
