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
from collections import namedtuple
from typing import ClassVar, Type

from django.conf import settings
from django.contrib import auth
from django.utils.module_loading import import_string
from rest_framework.authentication import BaseAuthentication

from apigw_manager.apigw.providers import PublicKeyProvider, SettingsPublicKeyProvider
from apigw_manager.apigw.utils import get_configuration


class ApiGatewayJWTAuthentication(BaseAuthentication):
    JWT_KEY_NAME = "HTTP_X_BKAPI_JWT"
    ALGORITHM = "RS512"
    PUBLIC_KEY_PROVIDER_CLS: ClassVar[Type[PublicKeyProvider]] = (
        SettingsPublicKeyProvider
    )

    App = namedtuple("App", ["bk_app_code", "verified"])

    def __init__(self):
        configuration = get_configuration()
        jwt_provider_cls = import_string(
            configuration.jwt_provider_cls
            or "apigw_manager.apigw.providers.DefaultJWTProvider"
        )
        self.provider = jwt_provider_cls(
            jwt_key_name=self.JWT_KEY_NAME,
            default_gateway_name=configuration.gateway_name,
            algorithm=getattr(settings, "APIGW_JWT_ALGORITHM", self.ALGORITHM),
            allow_invalid_jwt_token=getattr(
                settings, "APIGW_ALLOW_INVALID_JWT_TOKEN", False
            ),
            public_key_provider=self.PUBLIC_KEY_PROVIDER_CLS(
                default_gateway_name=configuration.gateway_name
            ),
        )

    def authenticate(self, request):
        jwt = self.provider.provide(request)
        if not jwt:
            return None

        request.jwt = jwt
        request._dont_enforce_csrf_checks = True

        jwt_app = (jwt.payload.get("app") or {}).copy()
        jwt_app.setdefault("bk_app_code", jwt_app.pop("app_code", None))

        request.app = self.make_app(**jwt_app)

        # skip when authenticated
        if hasattr(request, "user") and request.user.is_authenticated:
            return (request.user, None)

        jwt_user = (jwt.payload.get("user") or {}).copy()
        jwt_user.setdefault("bk_username", jwt_user.pop("username", None))

        user = self.get_user(request, gateway_name=jwt.gateway_name, **jwt_user)
        return (user, None)

    def authenticate_header(self, request):
        return self.JWT_KEY_NAME

    def make_app(self, bk_app_code=None, verified=False, **jwt_app):
        return self.App(
            bk_app_code=bk_app_code,
            verified=verified,
        )

    def get_user(
        self,
        request,
        gateway_name=None,
        bk_username=None,
        verified=False,
        **credentials
    ):
        # 传递 gateway_name 参数的用途：
        # 1. 来明确标识这个请求来自于网关
        # 2. 用户已经过认证，后端无需再认证
        # 3. 避免非预期调用激活对应后端使得用户认证被绕过
        return auth.authenticate(
            request,
            gateway_name=gateway_name,
            bk_username=bk_username,
            verified=verified,
            **credentials
        )
