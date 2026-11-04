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

# 可能包含凭证信息的请求头, 打印日志前需要脱敏
SENSITIVE_HEADERS = frozenset({"authorization", "proxy-authorization", "cookie"})


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
            if name.lower() in SENSITIVE_HEADERS:
                safe_request.headers[name] = "******"
        safe_request.body = None
        return curlify.to_curl(safe_request)
    except Exception:  # pylint: disable=broad-except
        return f"{request.method} {safe_url}"
