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
from collections import namedtuple

import jwt
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AnonymousUser
from django.core.cache import caches
from django.core.cache.backends.dummy import DummyCache

from apigw_manager.apigw.helper import PublicKeyManager
from apigw_manager.apigw.utils import get_configuration

logger = logging.getLogger(__name__)


class ApiGatewayJWTMiddleware:
    """
    The middleware reads the JWT header information transmitted by the API gateway,
    obtains the corresponding public key which to decrypt,
    decrypt the result to assign the value to the request.jwt.

    The algorithm that can be set by settings.APIGW_JWT_ALGORITHM,
    otherwise use the default value of the class definition

    By default, read the API gateway public key by settings.APIGW_PUBLIC_KEY.
    """

    JWT_KEY_NAME = 'HTTP_X_BKAPI_JWT'
    ALGORITHM = 'RS512'

    JWT = namedtuple("JWT", ["api_name", "payload"])

    def __init__(self, get_response):
        self.get_response = get_response

        configuration = get_configuration()
        self.default_api_name = configuration.api_name
        self.algorithm = getattr(settings, 'APIGW_JWT_ALGORITHM', self.ALGORITHM)

    def get_public_key(self, api_name):
        """Return the public key specified by Settings"""
        public_key = getattr(settings, 'APIGW_PUBLIC_KEY', None)
        if not public_key:
            logger.warning(
                'No `APIGW_PUBLIC_KEY` can be found in settings, you should either configure it '
                'with a valid value or remove `APIGatewayLoginMiddleware` middleware entirely'
            )
        return public_key

    def decode_jwt_header(self, jwt_payload):
        return jwt.get_unverified_header(jwt_payload)

    def decode_jwt(self, jwt_payload, public_key, algorithm):
        return jwt.decode(
            jwt_payload,
            public_key,
            algorithms=algorithm,
        )

    def __call__(self, request):
        jwt_payload = request.META.get(self.JWT_KEY_NAME, '')
        if not jwt_payload:
            return self.get_response(request)

        jwt_header = self.decode_jwt_header(jwt_payload)

        api_name = jwt_header.get("kid") or self.default_api_name
        public_key = self.get_public_key(api_name)
        if not public_key:
            logger.warning('no public key found')
            return self.get_response(request)

        algorithm = jwt_header.get("alg") or self.algorithm
        decoded = self.decode_jwt(
            jwt_payload,
            public_key,
            algorithm,
        )

        request.jwt = self.JWT(api_name=api_name, payload=decoded)
        # disable csrf checks
        request._dont_enforce_csrf_checks = True
        return self.get_response(request)


class ApiGatewayJWTGenericMiddleware(ApiGatewayJWTMiddleware):
    """
    This middleware is similar to ApiGatewayJWTMiddleware,
    but gets the API gateway public key from Context Model.

    settings.APIGW_JWT_PUBLIC_KEY_CACHE_MINUTES is used to set the public key cache expires,
    if the value is 0, it does not need to cache.

    settings.APIGW_JWT_PUBLIC_KEY_CACHE_NAME is the name of the cache instance.

    settings.APIGW_JWT_PUBLIC_KEY_CACHE_VERSION is the current version of cache.
    """

    CACHE_MINUTES = 0
    CACHE_NAME = 'default'
    CACHE_VERSION = '0'

    def __init__(self, get_response):
        super().__init__(get_response)
        self.cache_expires = getattr(settings, 'APIGW_JWT_PUBLIC_KEY_CACHE_MINUTES', self.CACHE_MINUTES) * 60
        self.cache_version = getattr(settings, 'APIGW_JWT_PUBLIC_KEY_CACHE_VERSION', self.CACHE_VERSION)

        cache_name = getattr(settings, 'APIGW_JWT_PUBLIC_KEY_CACHE_NAME', self.CACHE_NAME)

        # If the cache expires is 0, it does not need to cache
        if self.cache_expires:
            self.cache = caches[cache_name]
        else:
            self.cache = DummyCache(cache_name, params={})

    def get_public_key(self, api_name):
        """Get the specified public key from Context model, if not specified, return the default value"""
        cache_key = "apigw:public_key:%s" % api_name
        cached_value = self.cache.get(cache_key)
        if cached_value:
            return cached_value

        public_key = PublicKeyManager().get(api_name or self.default_api_name)
        if not public_key:
            return super(ApiGatewayJWTGenericMiddleware, self).get_public_key(api_name)

        self.cache.set(cache_key, public_key, self.cache_expires, self.cache_version)
        return public_key


class ApiGatewayJWTAppMiddleware:
    """Read the JWT information to set the request.app attribute"""

    App = namedtuple("App", ["bk_app_code", "verified"])

    def __init__(self, get_response):
        self.get_response = get_response

    def make_app(self, bk_app_code=None, verified=False, **jwt_app):
        return self.App(
            bk_app_code=bk_app_code,
            verified=verified,
        )

    def __call__(self, request):
        jwt_info = getattr(request, 'jwt', None)
        if not jwt_info:
            return self.get_response(request)

        jwt_app = (jwt_info.payload.get("app") or {}).copy()
        jwt_app.setdefault("bk_app_code", jwt_app.pop("app_code", None))

        request.app = self.make_app(**jwt_app)

        return self.get_response(request)


class ApiGatewayJWTUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def get_user(self, request, api_name=None, bk_username=None, verified=False, **credentials):
        # 传递 api_name 参数的用途：
        # 1. 来明确标识这个请求来自于网关
        # 2. 用户已经过认证，后端无需再认证
        # 3. 避免非预期调用激活对应后端使得用户认证被绕过
        return auth.authenticate(request, api_name=api_name, bk_username=bk_username, verified=verified, **credentials)

    def __call__(self, request):
        jwt_info = getattr(request, 'jwt', None)
        if not jwt_info:
            return self.get_response(request)

        # skip when authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self.get_response(request)

        jwt_user = (jwt_info.payload.get('user') or {}).copy()
        jwt_user.setdefault("bk_username", jwt_user.pop("username", None))

        request.user = self.get_user(request, api_name=jwt_info.api_name, **jwt_user)
        return self.get_response(request)


class UserModelBackend(ModelBackend):
    """Get users by username"""

    def __init__(self):
        super().__init__()

        user_model = get_user_model()

        if hasattr(user_model.objects, 'get_by_natural_key'):
            self.user_maker = user_model.objects.get_by_natural_key
        else:
            self.user_maker = lambda x: user_model.objects.filter(username=x).last()

    def make_anonymous_user(self, bk_username=None):
        user = AnonymousUser()
        user.username = bk_username
        return user

    def authenticate(self, request, api_name, bk_username, verified, **credentials):
        if not verified:
            return self.make_anonymous_user(bk_username=bk_username)
        return self.user_maker(bk_username)
