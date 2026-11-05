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

from typing import Any, Dict, Optional, Union
from urllib.parse import SplitResult, parse_qsl, unquote, urlsplit

# Placeholder for urls which can not be redacted reliably
REDACTED_URL_PLACEHOLDER = "<unparsable url>"


class MutableURL:
    _url: str
    _components: SplitResult
    _query: dict

    def __init__(self, url: Union[str, "MutableURL"]):
        if isinstance(url, MutableURL):
            self._url = url._url
        elif isinstance(url, str):
            self._url = url
        else:
            raise TypeError(f"Invalid type for MutableURL. Expected str or MutableURL, got {type(url)}")

    @property
    def components(self) -> SplitResult:
        if not hasattr(self, "_components"):
            self._components = urlsplit(self._url)
        return self._components

    @property
    def scheme(self):
        return self.components.scheme

    @property
    def username(self) -> Optional[str]:
        return self.components.username

    @property
    def password(self) -> Optional[str]:
        # Auto unescape password
        return unquote(self.components.password) if self.components.password else None

    @property
    def hostname(self) -> Optional[str]:
        return self.components.hostname

    @property
    def port(self) -> Optional[int]:
        return self.components.port

    @property
    def netloc(self) -> Optional[str]:
        return self.components.netloc

    @property
    def path(self) -> Optional[str]:
        return unquote(self.components.path) if self.components.path else None

    @property
    def query(self) -> Dict:
        if not hasattr(self, "_options"):
            self._query = dict(parse_qsl(self.components.query))
        return self._query

    def replace(self, **kwargs: Any) -> "MutableURL":
        if "username" in kwargs or "password" in kwargs or "hostname" in kwargs or "port" in kwargs:
            hostname = kwargs.pop("hostname", self.hostname)
            port = kwargs.pop("port", self.port)
            username = kwargs.pop("username", self.username)
            password = kwargs.pop("password", self.password)

            netloc = hostname
            if port is not None:
                netloc += f":{port}"
            if username is not None:
                userpass = username
                if password is not None:
                    userpass += f":{password}"
                netloc = f"{userpass}@{netloc}"

            kwargs["netloc"] = netloc

        components = self.components._replace(**kwargs)
        return self.__class__(components.geturl())

    def obscure(self) -> str:
        if self.password:
            return self.replace(password="********")._url
        return self._url

    def redacted(self) -> str:
        """Return a string which is safe to be logged. Only scheme, host, port and path are kept,
        userinfo, query and fragment are all dropped. This is best-effort: urls which are not
        well-formed are replaced with a fixed placeholder, so this method never raises.

        >>> MutableURL("redis://:password@localhost:6379/0?password=foo").redacted()
        'redis://localhost:6379/0'
        """
        url = self._url
        try:
            components = self.components
        except ValueError:
            return REDACTED_URL_PLACEHOLDER

        if not (
            url.isascii() and url.isprintable() and components.scheme and url.startswith(f"{components.scheme}://")
        ):
            return REDACTED_URL_PLACEHOLDER
        # "@" outside the netloc means the password contains unescaped "/", "?" or "#", the boundary
        # of userinfo can not be determined, e.g. "redis://:ab/cd@host:6379/0"
        if "@" in components.path + components.query + components.fragment:
            return REDACTED_URL_PLACEHOLDER
        # The last "@" in netloc is always the end of userinfo, the rest is "host:port"
        return f"{components.scheme}://{components.netloc.rpartition('@')[2]}{components.path}"

    def __str__(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.obscure())})"

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)
