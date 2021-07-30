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
from typing import List

from blue_krill.monitoring.probe.base import Issue, VirtualProbe

try:
    import redis
except ImportError as _e:
    raise ImportError('Error loading redis module: %s.\n' 'Did you install redis?' % _e) from _e


logger = logging.getLogger(__name__)


class RedisProbe(VirtualProbe):
    """
    Usage:
        class SomeRedisProbe(RedisProbe):
            name: str = "some"
            redis_url: str = "redis://localhost:6379/0"

    Example redis url::

        redis://[:password]@localhost:6379/0
        unix://[:password]@/path/to/socket.sock?db=0
    """

    redis_url: str

    def diagnose(self) -> List[Issue]:
        try:
            # from_url already used connection pool
            connection = redis.Redis.from_url(self.redis_url)
            connection.ping()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unknown Exception when connecting to %s", self.redis_url)
            return [Issue(fatal=True, description=str(e))]
        return []
