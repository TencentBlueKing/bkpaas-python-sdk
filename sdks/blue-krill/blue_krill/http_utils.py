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

import curlify
import requests

from blue_krill.data_types.url import MutableURL

# 名称中包含以下关键字的请求头可能携带凭证信息, 打印日志前需要脱敏,
# 如 Authorization、Proxy-Authorization、X-Bkapi-Authorization、Cookie、X-Api-Key、X-Token 等
SENSITIVE_HEADER_KEYWORDS = ("authorization", "cookie", "token", "secret", "password", "api-key", "apikey", "session")


def _is_sensitive_header(name: str) -> bool:
    lowered = name.lower()
    return any(keyword in lowered for keyword in SENSITIVE_HEADER_KEYWORDS)


def to_safe_curl(request: requests.PreparedRequest) -> str:
    """生成用于打印日志的等价 curl 命令。敏感请求头会被脱敏, 请求体（可能包含密码等信息）会被忽略,
    URL 中只保留 scheme、主机、端口与路径（userinfo 与查询参数中都可能包含凭证）。

    当无法生成 curl 命令时，退化为只返回请求方法和脱敏后的 URL。
    """
    safe_url = MutableURL(request.url or "").redacted()
    try:
        safe_request = request.copy()
        safe_request.url = safe_url
        for name in list(safe_request.headers):
            if _is_sensitive_header(name):
                safe_request.headers[name] = "******"
        safe_request.body = None
        return curlify.to_curl(safe_request)
    except Exception:  # pylint: disable=broad-except
        return f"{request.method} {safe_url}"
