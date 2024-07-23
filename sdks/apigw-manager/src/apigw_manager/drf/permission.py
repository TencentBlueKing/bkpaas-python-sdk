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

from rest_framework import permissions

logger = logging.getLogger(__name__)


class ApiGatewayPermission(permissions.BasePermission):
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
            if not hasattr(request, "app") or not request.app.verified:
                logger.error(
                    "can not found app in request or app is not verified, "
                    "make sure ApiGatewayJWTAppMiddleware is config in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES and incoming jwt is valid"
                )
                return False

        if getattr(view, "user_verified_required", False):
            if not hasattr(request, "user") or not request.user.is_authenticated:
                logger.error(
                    "can not found user in request or user is not authenticated, "
                    "make sure ApiGatewayJWTAuthentication is config in REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES and incoming jwt is valid"
                )
                return False

        return True
