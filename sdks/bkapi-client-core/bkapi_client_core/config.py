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
    from django.conf import settings as django_settings  # noqa
except ImportError:
    django_settings = None


class SettingKeys:
    """The defined setting keys"""

    APP_CODE = "BK_APP_CODE"
    APP_SECRET = "BK_APP_SECRET"

    # apigateway
    DEFAULT_STAGE_MAPPINGS = "BK_API_DEFAULT_STAGE_MAPPINGS"
    BK_API_CLIENT_ENABLE_SSL_VERIFY = "BK_API_CLIENT_ENABLE_SSL_VERIFY"
    BK_API_AUTHORIZATION_COOKIES_MAPPING = "BK_API_AUTHORIZATION_COOKIES_MAPPING"
    BK_API_URL_TMPL = "BK_API_URL_TMPL"

    # esb
    BK_COMPONENT_API_URL = "BK_COMPONENT_API_URL"
    DEFAULT_BK_API_VER = "DEFAULT_BK_API_VER"
    BK_API_USE_TEST_ENV = "BK_API_USE_TEST_ENV"


class Settings(object):
    def __init__(
        self,
        env=None,  # type: Optional[Dict[str, Any]]
        settings=None,  # type: Any
        aliases=None,  # type: Optional[Dict[str, List[str]]]
    ):
        self._aliases = aliases or {}  # type: Dict[str, List[str]]
        self._env = os.environ if env is None else env
        self._settings = django_settings if settings is None else settings
        self._defaults = {}  # type: Dict[str, Any]
        self._resolved = {}  # type: Dict[str, Any]

    def get(
        self,
        key,  # type: str
        default=None,  # type: Any
    ):
        # type: (...) -> Any
        """
        Returns the specified value, if not found, return to the default value
        """

        # If the key has been hold in the cache, return it directly
        if key in self._resolved:
            return self._resolved[key]

        for key in self._aliases.get(key, [key]):
            if self._settings and hasattr(self._settings, key):
                value = self._resolved[key] = getattr(self._settings, key)
                return value

            if self._env and key in self._env:
                value = self._resolved[key] = self._env[key]
                return value

            if key in self._defaults:
                value = self._resolved[key] = self._defaults[key]
                return value

        return default

    def set(self, key, value):
        """
        Set the value of the key
        """

        self._resolved[key] = value

    def set_defaults(self, defaults_):
        """
        Set the default value of the key
        """
        if defaults_:
            self._defaults.update(defaults_)

    def reset(self):
        """
        Reset the resolved cache
        """

        self._resolved.clear()

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
        SettingKeys.APP_CODE: ["BK_APP_CODE", "APP_CODE"],
        SettingKeys.APP_SECRET: ["BK_APP_SECRET", "SECRET_KEY"],
    }
)

settings.set_defaults(
    {
        SettingKeys.DEFAULT_BK_API_VER: "v2",
        SettingKeys.BK_API_USE_TEST_ENV: False,
        SettingKeys.BK_API_CLIENT_ENABLE_SSL_VERIFY: True,
    }
)
