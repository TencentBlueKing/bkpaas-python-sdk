# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import yaml

from typing import Dict, List, Optional, Tuple


def build_bk_header_rewrite(set: Dict[str, str], remove: List[str]) -> Dict[str, str]:
    return {
        "type": "bk-header-rewrite",
        "yaml": yaml.dump(
            {
                "set": [{"key": k, "value": v} for k, v in set.items()],
                "remove": [{"key": k} for k in remove],
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
    if allow_credential and (allow_origins == "*" or allow_methods == "*" or allow_headers == "*"):
        raise ValueError("allow_credential can not be True when allow_origins/allow_methods/allow_headers is '*'")

    if allow_origins and allow_origins_by_regex:
        raise ValueError("allow_origins and allow_origins_by_regex can not be set at the same time")

    return {
        "type": "bk-cors",
        "yaml": yaml.dump(
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
    message: str = "Your IP is not allowed",
) -> Dict[str, str]:
    if whitelist and blacklist:
        raise ValueError("whitelist and blacklist can not be set at the same time")

    if not whitelist:
        whitelist = []
    if not blacklist:
        blacklist = []

    return {
        "type": "bk-ip-restriction",
        "yaml": yaml.dump(
            {
                "whitelist": "\n".join(whitelist),
                "blacklist": "\n".join(blacklist),
                "message": message,
            }
        ),
    }
    # GOT: "yaml": "whitelist: |- '127.0.0.1\n\n  192.168.2.1'\nmessage: IP not allowed\nwhitelist: ''\n",
    # whitelist: |-\n  127.0.0.1\n\n  192.111.1.1

    # pluginConfigs:
    # - type: bk-ip-restriction
    #   yaml: |-
    #     whitelist: |-
    #       127.0.0.1
    #       #abcd
    #       192.169.1.1/24


def build_bk_rate_limit(
    default_period: int, default_tokens: int, specific_app_limits: Optional[List[Tuple[str, int, int]]]
) -> Dict[str, str]:
    # TODO: period to 1 / 60 / 3600 / 86400
    # TODO: specific_app_limits do some check?
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
            rates[app_code] = [
                {
                    "period": period,
                    "tokens": tokens,
                }
            ]
    return {
        "type": "bk-rate-limit",
        "yaml": yaml.dump(
            {
                "rates": rates,
            }
        ),
    }


# TODO:
# 1. add bk-ip-restriction plugin, make it right
# 2. add validator for all pluginConfigs
# 3. add unittest
