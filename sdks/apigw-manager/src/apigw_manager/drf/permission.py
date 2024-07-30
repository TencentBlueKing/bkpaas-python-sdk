# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import logging

from rest_framework import permissions

logger = logging.getLogger(__name__)


class ApiGatewayPermission(permissions.BasePermission):
    """this permission is used to check if the request is from apigateway

    if the view has `FROM_APIGW_EXEMPT` attribute, then the permission will be exempted
    otherwise:
    1. check if the request has jwt, if not, return False
    2. check if the view has `app_verified_required` attribute, if yes, check if the request has app and app is verified
    3. check if the view has `user_verified_required` attribute, if yes, check if the request has user and user is authenticated
    """

    def has_permission(self, request, view):
        exempt = getattr(view, "FROM_APIGW_EXEMPT", False)
        if exempt:
            return True

        if not hasattr(request, "jwt"):
            logger.error(
                "can not found jwt in request, "
                "make sure ApiGatewayJWTAuthentication is config in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES and incoming jwt is valid"
            )
            return False

        logger.debug("request.jwt.payload: %s", request.jwt.payload)

        if getattr(view, "app_verified_required", False):
            if not hasattr(request, "app"):
                logger.error(
                    "can not found app in request, "
                    "make sure ApiGatewayJWTAppMiddleware is config in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES and incoming jwt is valid"
                )
                return False

            if not request.app.verified:
                logger.error(
                    "found app in request but the app is not verified, "
                    "make sure ApiGatewayJWTAppMiddleware is config in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES and incoming jwt is valid"
                )
                return False

        if getattr(view, "user_verified_required", False):
            if not hasattr(request, "user"):
                logger.error(
                    "can not found user in request, "
                    "make sure ApiGatewayJWTAuthentication is config in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES and incoming jwt is valid"
                )
                return False

            if not request.user.is_authenticated:
                logger.error(
                    "found user in request but the user is not authenticated, "
                    "make sure ApiGatewayJWTAuthentication is config in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES and incoming jwt is valid"
                )
                return False

        return True
