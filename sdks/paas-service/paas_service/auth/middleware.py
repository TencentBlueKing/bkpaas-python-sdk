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
from typing import Optional

from .backends import AuthFailedError, JWTClientAuthenticator

logger = logging.getLogger(__name__)


class VerifiedClientMiddleware(object):
    """This middleware will inject request.verified_client if current request has a valid
    signed JWT token in request headers
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def get_token(request) -> Optional[str]:
        """Get token from request, return None if no token can be found"""
        auth_header_val = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header_val:
            return None

        try:
            prefix, token = auth_header_val.split(None, 1)
        except ValueError:
            logger.warning('Invalid authorization header value')
            return None

        return token

    def __call__(self, request):
        token = self.get_token(request)
        request.client = None
        if token:
            try:
                ret = JWTClientAuthenticator().authenticate(token=token)
                request.client = ret.client
            except AuthFailedError:
                pass

        response = self.get_response(request)
        return response
