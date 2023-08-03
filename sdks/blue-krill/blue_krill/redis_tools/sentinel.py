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
from typing import Any, Dict, List, Optional, Union

from django.utils.functional import cached_property

from blue_krill.data_types.url import MutableURL

try:
    import redis
    from redis import sentinel  # noqa
except ImportError as _e:
    raise ImportError('Error loading redis module: %s.\n' 'Did you install a suitable version for redis?' % _e) from _e

SentinelHost = Dict[str, Optional[Union[str, int]]]


class SentinelBackend:
    """Redis Sentinel Backend"""

    def __init__(self, url: str, master_name: str, sentinel_kwargs: Dict[str, Any], **connection_kwargs):
        """
        :param url: 格式如 sentinel://0.0.0.0:26347/3;sentinel://0.0.0.0:26347/3
        :param master_name: sentinel service name
        :param sentinel_kwargs: sentinel 相关配置, 如 password, master_name 等
        :param connection_kwargs: redis 连接设置
        """
        self.master_name = master_name
        self.sentinel_kwargs = sentinel_kwargs
        self.connection_kwargs = connection_kwargs or {}
        self._parse_from_url(url)

    @property
    def hosts(self) -> List[SentinelHost]:
        return self._hosts

    @property
    def password(self) -> Optional[str]:
        """redis 实例密码, 非 sentinel 密码"""
        return self._password

    @property
    def db(self) -> int:
        return self._db

    @cached_property
    def client(self) -> redis.Redis:
        self.connection_kwargs['db'] = self.db
        if self.password:
            self.connection_kwargs['password'] = self.password

        sentinel_instance = sentinel.Sentinel(
            [(cp['host'], cp['port']) for cp in self.hosts],
            sentinel_kwargs=self.sentinel_kwargs,
            **self.connection_kwargs,
        )
        return sentinel_instance.master_for(service_name=self.master_name)

    def _parse_from_url(self, url: str):
        """从 url 解析出主机端口等信息"""
        chunks = url.split(';')

        parts = MutableURL(url=chunks[0])
        self._validate_scheme(parts.scheme)
        hosts = [{'host': parts.hostname, 'port': parts.port}]

        self._db = self._extract_db(parts.path)
        self._password = parts.password

        for chunk in chunks[1:]:
            parts = MutableURL(url=chunk)
            self._validate_scheme(parts.scheme)
            hosts.append({'host': parts.hostname, 'port': parts.port})

        self._hosts = hosts

    def _extract_db(self, path: Optional[str]) -> int:
        """从 url path 中提取 redis db.

        :param path: url path
        :return: redis db num. 如果从 path 中无法解析出合法的 db num, 直接返回0
        """
        if not path:
            return 0

        if path.startswith('/'):
            path = path[1:]

        try:
            return int(path)
        except (ValueError, TypeError):
            return 0

    def _validate_scheme(self, scheme: str):
        if scheme != 'sentinel':
            raise ValueError('url must be sentinel scheme')
