# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import logging
from binascii import Error as PaddingError
from typing import Any

import jwt
from jwt.utils import base64url_decode

from blue_krill.text import mask_secret

logger = logging.getLogger(__name__)

# The claims are not verified when describing a token and may be crafted by anyone, so limit their length
_MAX_CLAIM_LENGTH = 64


def validate_jwt_token(s: str) -> bool:
    """
    Test if a given string might be a JWT token, more on JWT: https://jwt.io/introduction
    """
    parts = s.split(".")
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


def describe_token(token: str) -> str:
    """Describe a JWT token for logging. The token itself is never logged, only the unverified "iss" and
    "expires_at" claims and the masked signature are included. Never raises, if the claims can not be
    decoded, only the masked signature is returned.
    """
    signature = mask_secret(token.rsplit(".", 1)[-1])
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        iss, expires_at = (_format_claim(payload.get(name)) for name in ("iss", "expires_at"))
    except Exception:  # pylint: disable=broad-except
        return f"signature={signature}"
    return f"iss={iss}, expires_at={expires_at}, signature={signature}"


def _format_claim(value: Any) -> str:
    """Format an unverified claim for logging, use repr to escape special characters such as line breaks"""
    if value is None:
        return "None"
    return repr(str(value)[:_MAX_CLAIM_LENGTH])


def get_paas_service_jwt_clients():
    try:
        from django.conf import settings
    except ImportError:
        logger.exception("you should supply paas service jwt clients")
        raise
    else:
        return settings.PAAS_SERVICE_JWT_CLIENTS
