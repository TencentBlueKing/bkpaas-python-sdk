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
from typing import Optional

from cryptography.fernet import Fernet

from blue_krill.encoding import force_bytes, force_text

logger = logging.getLogger(__name__)


def get_default_secret_key():
    try:
        from django.conf import settings

        return settings.BKKRILL_ENCRYPT_SECRET_KEY
    except ImportError:
        logger.exception("you should supply a default secret key")
        raise


def encrypt_string(s: str, key: Optional[bytes] = None) -> str:
    """Shortcut function: encrypt a string into a fernet token"""
    key = key or get_default_secret_key()
    f = Fernet(key)
    value = f.encrypt(force_bytes(s))
    return force_text(value)


def decrypt_string(s: str, key: Optional[bytes] = None) -> str:
    """Shortcut function: decrypt a fernet token into a string"""
    key = key or get_default_secret_key()
    f = Fernet(key)
    value = f.decrypt(force_bytes(s))
    return force_text(value)
