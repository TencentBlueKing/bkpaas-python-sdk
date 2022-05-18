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
from binascii import Error as PaddingError

from jwt.utils import base64url_decode

logger = logging.getLogger(__name__)


def validate_jwt_token(s: str) -> bool:
    """
    Test if a given string might be a JWT token, more on JWT: https://jwt.io/introduction
    """
    parts = s.split('.')
    if len(parts) != 3:
        return False

    try:
        # JWT: {header}.{payload}.{signature}
        # The "header" and "payload" parts were always b64encoded
        base64url_decode(parts[0])
        base64url_decode(parts[1])
    except (PaddingError, ValueError):
        return False
    return True


def get_paas_service_jwt_clients():
    try:
        from django.conf import settings

        return settings.PAAS_SERVICE_JWT_CLIENTS
    except ImportError:
        logger.exception("you should supply paas service jwt clients")
        raise
