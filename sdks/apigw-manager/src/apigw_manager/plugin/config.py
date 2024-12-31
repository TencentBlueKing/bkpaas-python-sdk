# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 蓝鲸 PaaS 平台 (BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import ipaddress
from typing import Dict, List, Optional, Tuple

from .utils import literal_unicode, yaml_dump, yaml_text_indent


def build_bk_header_rewrite(set: Dict[str, str], remove: List[str]) -> Dict[str, str]:
    """generate bk-header-rewrite plugin config

    Args:
        set (Dict[str, str]): the key-value pair to set header
        remove (List[str]): the key list to remove header

    Raises:
        ValueError: key {} can not contain ':'

    Returns:
        {
            "type": "bk-header-rewrite",
            "yaml": "set:\n  - key: key1\n    value: value1\n  - key: key2\n    value: value2\nremove:\n  - key1\n"
        }
    """
    set_data = []
    for k, v in set.items():
        if ":" in k:
            raise ValueError(f"key {k} can not contain ':'")
        set_data.append({"key": k, "value": v})

    remove_data = []
    for k in remove:
        if ":" in k:
            raise ValueError(f"key {k} can not contain ':'")
        remove_data.append({"key": k})

    return {
        "type": "bk-header-rewrite",
        "yaml": yaml_dump(
            {
                "set": set_data,
                "remove": remove_data,
            }
        ),
    }


def build_bk_cors(
    allow_origins: str = "*",
    allow_origins_by_regex: Optional[List[str]] = None,
    allow_methods: str = "*",
    allow_headers: str = "*",
    expose_headers: str = "*",
    max_age: int = 86400,
    allow_credential: bool = False,
):
    """generate bk-cors plugin config

    Args:
        allow_origins (str, optional): 允许跨域访问的 Origin. Defaults to "*".
            - 格式为 scheme://host:port，示例如 https://example.com:8081。如果你有多个 Origin，请使用 , 分隔。
            - 当 allow_credential 为 false 时，可以使用 * 来表示允许所有 Origin 通过。
            - 你也可以在启用了 allow_credential 后使用 ** 强制允许所有 Origin 均通过，但请注意这样存在安全隐患。
            - allow_origins、allow_origins_by_regex 只能一个有效
        allow_origins_by_regex (Optional[List[str]], optional): 使用正则表示的允许跨域访问的 Origin. Defaults to None.
            - 示例如 '^https://.*\\.example\\.com:8081$'，此正则允许 https://a.example.com:8081, https://b.example.com:8081。
            - allow_origins、allow_origins_by_regex 只能一个有效。
        allow_methods (str, optional): 允许跨域访问的 Method. Defaults to "*".
            - 比如：GET，POST 等。如果你有多个 Method，请使用 , 分割。
            - 当 allow_credential 为 false 时，可以使用 * 来表示允许所有 Method 通过。
            - 你也可以在启用了 allow_credential 后使用 ** 强制允许所有 Method 都通过，但请注意这样存在安全隐患。
        allow_headers (str, optional): 允许跨域访问时请求方携带哪些非 CORS 规范 以外的 Header. Defaults to "*".
            - 如果你有多个 Header，请使用 , 分割。
            - 当 allow_credential 为 false 时，可以使用 * 来表示允许所有 Header 通过。
            - 你也可以在启用了 allow_credential 后使用 ** 强制允许所有 Header 都通过，但请注意这样存在安全隐患。
        expose_headers (str, optional): 允许跨域访问时响应方携带哪些非 CORS 规范 以外的 Header. Defaults to "*".
            - 如果你有多个 Header，请使用 , 分割。
            - 当 allow_credential 为 false 时，可以使用 * 来表示允许任意 Header。
            - 你也可以在启用了 allow_credential 后使用 ** 强制允许任意 Header，但请注意这样存在安全隐患
        max_age (int, optional): 浏览器缓存 CORS 结果的最大时间，单位为秒。Defaults to 86400.
            - 在这个时间范围内，浏览器会复用上一次的检查结果，-1 表示不缓存。请注意各个浏览器允许的最大时间不同。
        allow_credential (bool, optional): 是否允许跨域访问的请求方携带凭据（如 Cookie 等）. Defaults to False.
            - 根据 CORS 规范，如果设置该选项为 true，那么将不能在其他属性中使用 *。

    Raises:
        ValueError: allow_credential can not be True when allow_origins/allow_methods/allow_headers is '*'
        ValueError: allow_origins and allow_origins_by_regex can not be set at the same time

    Returns:
        {
            "type": "bk-cors",
            "yaml": "allow_origins: '*'\nallow_origins_by_regex: null\nallow_methods: '*'\nallow_headers: '*'\nexpose_headers: '*'\nmax_age: 86400\nallow_credential: false"
        }
    """
    if allow_credential and (allow_origins == "*" or allow_methods == "*" or allow_headers == "*"):
        raise ValueError("allow_credential can not be True when allow_origins/allow_methods/allow_headers is '*'")

    if allow_origins and allow_origins_by_regex:
        raise ValueError("allow_origins and allow_origins_by_regex can not be set at the same time")

    if allow_methods != "*" and allow_methods != "**":
        methods = allow_methods.split(",")
        for m in methods:
            if m not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE", "CONNECT"]:
                raise ValueError(f"invalid method {m}")

    return {
        "type": "bk-cors",
        "yaml": yaml_dump(
            {
                "allow_origins": allow_origins,
                "allow_origins_by_regex": allow_origins_by_regex,
                "allow_methods": allow_methods,
                "allow_headers": allow_headers,
                "expose_headers": expose_headers,
                "max_age": max_age,
                "allow_credential": allow_credential,
            }
        ),
    }


def build_bk_ip_restriction(
    whitelist: Optional[List[str]] = None,
    blacklist: Optional[List[str]] = None,
) -> Dict[str, str]:
    """generate bk-ip-restriction plugin config

    Args:
        whitelist (Optional[List[str]], optional): 白名单，ip 列表或 cidr 列表。Defaults to None.
        blacklist (Optional[List[str]], optional): 黑名单，ip 列表或 cidr 列表。Defaults to None.

    Raises:
        ValueError: whitelist and blacklist can not be set at the same time
        ValueError: whitelist or blacklist should be set
    Returns:
        {
            "type": "bk-ip-restriction",
            "yaml": "whitelist: |- 127.0.0.1"
        }
    """
    if whitelist and blacklist:
        raise ValueError("whitelist and blacklist can not be set at the same time")

    if not (whitelist or blacklist):
        raise ValueError("whitelist or blacklist should be set")

    if not whitelist:
        whitelist = []
    if not blacklist:
        blacklist = []

    # validate the ips
    if whitelist:
        [ipaddress.ip_interface(ip) for ip in whitelist]
        return {
            "type": "bk-ip-restriction",
            "yaml": yaml_dump(
                {
                    "whitelist": literal_unicode("\n".join(whitelist)),
                },
            ),
        }

    if blacklist:
        [ipaddress.ip_interface(ip) for ip in blacklist]
        return {
            "type": "bk-ip-restriction",
            "yaml": yaml_dump(
                {
                    "blacklist": literal_unicode("\n".join(blacklist)),
                },
            ),
        }

    return {}


VALID_PERIODS = [1, 60, 3600, 86400]


def build_bk_rate_limit(
    default_period: int, default_tokens: int, specific_app_limits: Optional[List[Tuple[str, int, int]]]
) -> Dict[str, str]:
    """generate bk-rate-limit plugin config

    Args:
        default_period (int): 默认的限流周期，单位为秒。有效值为 1 (seconds)/ 60 (minute)/ 3600 (hour)/ 86400 (day)
        default_tokens (int): 默认的限流令牌数
        specific_app_limits (Optional[List[Tuple[str, int, int]]]): 特殊应用的限流配置，格式为 [(app_code, period, tokens), ...]

    Raises:
        ValueError: default_period should be 1 (seconds)/ 60 (minute)/ 3600 (hour)/ 86400 (day)
        ValueError: period of {app_code} should be 1 (seconds)/ 60 (minute)/ 3600 (hour)/ 86400 (day)

    Returns:
        {
            "type": "bk-rate-limit",
            "yaml": "rates:\n  __default:\n    - period: 1\n      tokens: 10\n  app_code:\n    - period: 1\n      tokens: 10"
        }
    """
    if default_period not in VALID_PERIODS:
        raise ValueError("default_period should be 1 (seconds)/ 60 (minute)/ 3600 (hour)/ 86400 (day)")

    rates = {
        "__default": [
            {
                "period": default_period,
                "tokens": default_tokens,
            }
        ]
    }
    if specific_app_limits:
        for app_code, period, tokens in specific_app_limits:
            if period not in VALID_PERIODS:
                raise ValueError(f"period of {app_code} should be 1 (seconds)/ 60 (minute)/ 3600 (hour)/ 86400 (day)")
            rates[app_code] = [
                {
                    "period": period,
                    "tokens": tokens,
                }
            ]

    return {
        "type": "bk-rate-limit",
        "yaml": yaml_dump(
            {
                "rates": rates,
            }
        ),
    }


def build_stage_plugin_config_for_definition_yaml(
    plugin_configs: List[Dict[str, str]], indent: int = 10
) -> List[Dict[str, str]]:
    """generate stage plugin config for definition yaml, it would include with indent

    Args:
        plugin_configs (List[Dict[str, str]]): the plugin config list

    Returns:
        {
            "type": "stage",
            "yaml": "pre: |- set:\n  - key: key1\n    value: value1\n  - key: key2\n    value: value2\nremove:\n  - key1\n"
        }
    """
    indented_plugin_configs: List[Dict[str, str]] = []
    for plugin_config in plugin_configs:
        _type = plugin_config["type"]
        yaml = plugin_config["yaml"]
        indented_yaml = yaml_text_indent(yaml, indent)

        indented_plugin_configs.append(
            {
                "type": _type,
                "yaml": indented_yaml,
            }
        )
    return indented_plugin_configs
