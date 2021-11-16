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
import os
from typing import Any, Dict, List, Optional

try:
    from django.conf import settings as django_settings
except ImportError:
    django_settings = None


class Settings(object):
    def __init__(
        self,
        env=None,  # type: Optional[Dict[str, Any]]
        settings=None,  # type: Any
        aliases=None,  # type: Dict[str, List[str]]
    ):
        self._aliases = aliases or {}  # type: Dict[str, List[str]]
        self._env = os.environ if env is None else env
        self._settings = django_settings if settings is None else settings

    def get(
        self,
        key,  # type: str
        default=None,  # type: Any
    ):
        """
        Returns the specified value, if not found, return to the default value
        """

        for key in self._aliases.get(key, [key]):
            if self._settings and hasattr(self._settings, key):
                return getattr(self._settings, key)

            if self._env and key in self._env:
                return self._env[key]

        return default

    def declare_aliases(
        self,
        key,  # type: str
        aliases,  # type: List[str]
    ):
        """
        Declare an alias of a Key
        """

        self._aliases[key] = aliases


settings = Settings(
    aliases={
        "BK_APP_CODE": ["BK_APP_CODE", "APP_CODE"],
        "BK_APP_SECRET": ["BK_APP_SECRET", "SECRET_KEY"],
    }
)
