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
import time
from dataclasses import dataclass
from typing import Dict, Optional

import jwt
from requests.auth import AuthBase

logger = logging.getLogger(__name__)


@dataclass
class JWTAuthConf:
    """JWT conf object

    :param extra_payload: extra key value pairs in generated payload
    """

    iss: str
    key: str
    algorithm: str
    extra_payload: Optional[Dict] = None


class ClientJWTAuth(AuthBase):
    """Auto sign and inject a JWT token in the request headers

    :param auth_conf: JWT Auth instance
    :param prefix: Prefix string of header, default to "Bearer"
    :param expires_in: After how many seconds, token will be considered expired, default to 3600
    """

    _default_expires_in = 3600

    def __init__(self, auth_conf: JWTAuthConf, prefix: str = 'Bearer', expires_in: int = None):
        self.auth_conf = auth_conf
        self.prefix = prefix
        self.expires_in = expires_in or self._default_expires_in

    def __call__(self, r):
        payload = {
            'iss': self.auth_conf.iss,
            'expires_at': time.time() + self.expires_in,
        }
        # Mix extra payload content
        payload.update(self.auth_conf.extra_payload or {})

        token = jwt.encode(payload, key=self.auth_conf.key, algorithm=self.auth_conf.algorithm).decode()
        r.headers['Authorization'] = f'{self.prefix} {token}'
        logger.debug(f"got remote services' jwt header: {r.headers}")
        return r
