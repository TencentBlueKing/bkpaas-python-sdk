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
from django.http import JsonResponse


def jwt_info(request):
    data = {}
    jwt = getattr(request, 'jwt', None)
    if jwt:
        data.update(
            {
                "api_name": request.jwt.api_name,
                "payload": request.jwt.payload,
            }
        )

    return JsonResponse(data)


def jwt_app(request):
    data = {}
    app = getattr(request, 'app', None)
    if app:
        data.update(
            {
                "bk_app_code": app.bk_app_code,
                "verified": app.verified,
            }
        )

    return JsonResponse(data)


def jwt_user(request):
    data = {}
    user = getattr(request, 'user', None)
    if user:
        data.update(
            {
                "username": user.username,
                "is_anonymous": user.is_anonymous,
            }
        )

    return JsonResponse(data)
