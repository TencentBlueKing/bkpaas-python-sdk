# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 蓝鲸 PaaS 平台 (BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import ast
import json
import jsonschema
import ipaddress
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


from .constants import Draft7Schema
from .utils import literal_unicode, yaml_dump, yaml_text_indent


VARS_ALLOWED_COMPARISON_SYMBOLS = {"==", "~=", ">", ">=", "<", "<=", "~~", "~*", "in", "has", "!", "ipmatch"}


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


def build_bk_mock(
    response_example: str,
    response_headers: Dict[str, str],
    response_status: int = 200,
) -> Dict[str, str]:
    """generate bk-mock plugin config

    Args:
        response_example (str): 响应体。
        response_headers (Dict[str, str]): 响应头。
        response_status (int, optional): 响应状态码。Defaults to 200.

    Raises:
        ValueError: response_status cannot be less than 100
        ValueError: key {} can not contain ':'

    Returns:
        {
            "type": "bk-mock",
            "yaml": "response_headers:\n- key: key1\nvalue: value1\n- key: key2\nvalue: value2\nresponse_status: 200\nresponse_example: ''"
        }
    """
    if response_status < 100:
        raise ValueError("response_status cannot be less than 100")

    response_header_data = []
    for k, v in response_headers.items():
        if ":" in k:
            raise ValueError(f"key {k} can not contain ':'")
        response_header_data.append({"key": k, "value": v})

    return {
        "type": "bk-mock",
        "yaml": yaml_dump(
            {
                "response_example": response_example,
                "response_headers": response_header_data,
                "response_status": response_status,
            }
        ),
    }


@dataclass
class UnhealthyConfig:
    http_statuses: List[int] = None
    failures: int = 3


@dataclass
class HealthyConfig:
    http_statuses: List[int] = None
    successes: int = 3


def build_api_breaker(
    break_response_body: str,
    break_response_headers: Dict[str, str],
    unhealthy: UnhealthyConfig,
    healthy: HealthyConfig,
    break_response_code: int = 502,
    max_breaker_sec: int = 300,
) -> Dict[str, str]:
    """generate api-breaker plugin config

    Args:
        break_response_body (str): 当上游服务处于不健康状态时返回的 HTTP 响应体信息。
        break_response_headers (Dict[str, str]): 当上游服务处于不健康状态时返回的 HTTP 响应头信息。
        unhealthy (UnhealthyConfig): 当上游服务处于不健康状态时的 HTTP 的状态码和异常请求次数。
            - 应包含键 "http_statuses"(不健康状态码列表)和"failures"(触发不健康状态的异常请求次数)
        healthy (HealthyConfig): 上游服务处于健康状态时的 HTTP 状态码和连续正常请求次数。
            - 应包含键 "http_statuses"(健康状态码列表)和"successes"(触发健康状态的连续正常请求次数)
        break_response_code (int, optional): 当上游服务处于不健康状态时返回的 HTTP 错误码。Defaults to 502.
        max_breaker_sec (int, optional): 上游服务熔断的最大持续时间，以秒为单位，最小 3 秒。Defaults to 300.

    Raises:
        ValueError: max_breaker_sec duration cannot be less than 3 seconds
        ValueError: unhealthy status must be between 500 and 599
        ValueError: unhealthy failures must be greater than or equal to 1
        ValueError: healthy status must be between 200 and 499
        ValueError: healthy successes must be greater than or equal to 1
        ValueError: key {} can not contain ':'

    Returns:
        {
            "type": "api-breaker",
            "yaml": "break_response_code: 502\nbreak_response_body: ''\nbreak_response_headers:\n  - key: key1\n    value: value1\nmax_breaker_sec: 300\nunhealthy:\n  http_statuses:\n    - 503\n  failures: 3\nhealthy:\n  http_statuses:\n    - 200\n  successes: 3"
        }
    """

    if break_response_code is None:
        raise ValueError("break_response_code is required")

    if not (200 <= break_response_code <= 599):
        raise ValueError("break_response_code must be between 200 and 599")

    if max_breaker_sec and max_breaker_sec < 3:
        raise ValueError("max_breaker_sec duration cannot be less than 3 seconds")

    unhealthy_http_statuses = unhealthy.http_statuses or [500]
    for status in unhealthy_http_statuses:
        if not (500 <= status <= 599):
            raise ValueError("unhealthy status must be between 500 and 599")

    unhealthy_failures = unhealthy.failures
    if unhealthy_failures is not None and unhealthy_failures < 1:
        raise ValueError("unhealthy failures must be greater than or equal to 1")

    healthy_http_statuses = healthy.http_statuses or [200]
    for status in healthy_http_statuses:
        if not (200 <= status <= 499):
            raise ValueError("healthy status must be between 200 and 499")

    healthy_successes = healthy.successes
    if healthy_successes is not None and healthy_successes < 1:
        raise ValueError("healthy successes must be greater than or equal to 1")

    break_response_header_data = []
    for k, v in break_response_headers.items():
        if ":" in k:
            raise ValueError(f"key {k} can not contain ':'")
        break_response_header_data.append({"key": k, "value": v})

    return {
        "type": "api-breaker",
        "yaml": yaml_dump(
            {
                "break_response_code": break_response_code,
                "break_response_body": break_response_body,
                "break_response_headers": break_response_header_data,
                "max_breaker_sec": max_breaker_sec,
                "unhealthy": {
                    "http_statuses": unhealthy_http_statuses,
                    "failures": unhealthy_failures
                },
                "healthy": {
                    "http_statuses": healthy_http_statuses,
                    "successes": healthy_successes
                },
            }
        ),
    }


@dataclass
class AbortConfig:
    http_status: int
    body: str
    percentage: int
    vars: str


@dataclass
class DelayConfig:
    duration: float
    percentage: int
    vars: str


def build_fault_injection(
    abort: Optional[AbortConfig] = None,
    delay: Optional[DelayConfig] = None,
) -> Dict[str, str]:
    """generate fault-injection plugin config

    Args:
        abort (AbortConfig, optional): 中断状态。
            - http_status (int): 返回给客户端的 HTTP 状态码。
            - body (str): 返回给客户端的响应数据。支持使用 NGINX 变量，如 client addr: $remote_addr\n。
            - percentage (int): 将被中断的请求占比(0-100)。
            - vars (str): 执行故障注入的规则，当规则匹配通过后才会执行故障注。vars 是一个表达式的列表，来自 lua-resty-expr。
        delay (DelayConfig, optional): 延迟状态。
            - duration (number): 延迟时间，单位秒，只能填入整数。
            - percentage (int): 将被延迟的请求占比(0-100)
            - vars (str): 执行请求延迟的规则，当规则匹配通过后才会延迟请求。vars 是一个表达式列表，来自 lua-resty-expr。

    Raises:
        ValueError: At least one of the conditions 'abort' or 'delay' must be configured
        ValueError: http_status is required in abort
        ValueError: http_status must be greater than 200
        ValueError: The percentage of abort must be greater than 0 and less than or equal to 100
        ValueError: duration is required in delay

    Returns:
        {
            "type": "fault-injection",
            "yaml": "abort:\n  body: ''\n  http_status: 500\n  percentage: 20\n  vars: ''\ndelay:\n  duration: 2.5\n  percentage: 100\n  vars: ''\n"
        }
    """
    config = {}

    if not abort and not delay:
        raise ValueError("At least one of the conditions 'abort' or 'delay' must be configured")

    if abort:
        http_status = abort.http_status
        if not http_status:
            raise ValueError("http_status is required in abort")
        if http_status < 200:
            raise ValueError("http_status must be greater than 200")

        percentage = abort.percentage
        _check_percentage(percentage, "abort")

        abort_vars = abort.vars
        if abort_vars:
            _check_vars(abort_vars, "abort")

        config["abort"] = {
            "http_status": http_status,
            "body": abort.body,
            "percentage": percentage,
            "vars": abort_vars
        }

    if delay:
        if not delay.duration:
            raise ValueError("duration is required in delay")

        percentage = delay.percentage
        _check_percentage(percentage, "delay")

        delay_vars = delay.vars
        if delay_vars:
            _check_vars(delay_vars, "delay")

        config["delay"] = {
            "duration": delay.duration,
            "percentage": percentage,
            "vars": delay_vars
        }

    return {
        "type": "fault-injection",
        "yaml": yaml_dump(config)
    }


def build_request_validation(
        body_schema: str,
        header_schema: str,
        rejected_msg: str,
        rejected_code: int = 400,
) -> Dict[str, str]:
    """generate request-validation plugin config

    Args:
        body_schema (str): request body 数据的 JSON Schema。
        header_schema (str): request header 数据的 JSON Schema。
        rejected_msg (str): 拒绝信息。
        rejected_code (int, optional): 拒绝状态码。Defaults to 400.

    Raises:
        ValueError: rejected_code must be between 200 and 599
        ValueError: header_schema or body_schema should be configured at least one
        ValueError: Your {schema_name} Schema is not a valid JSON
        ValueError: Your {schema_name} Schema is not valid: {err}

    Returns:
        {
            "type": "request-validation",
            "yaml": 'body_schema: \'{"type": "object"}\'\nheader_schema: \'{"type": "object"}\'\nrejected_code: 403\nrejected_msg: test\n'
        }
    """
    config = {
        "rejected_code": rejected_code,
        "rejected_msg": rejected_msg
    }

    if not (200 <= rejected_code <= 599):
        raise ValueError("rejected_code must be between 200 and 599")

    if not body_schema and not header_schema:
        raise ValueError("header_schema or body_schema should be configured at least one")

    if body_schema:
        _validate_json_schema("body_schema", body_schema)
        config["body_schema"] = body_schema

    if header_schema:
        _validate_json_schema("header_schema", header_schema)
        config["header_schema"] = header_schema

    return {
        "type": "request-validation",
        "yaml": yaml_dump(config)
    }


@dataclass
class HeadersConfig:
    add: Dict[str, str]
    set: Dict[str, str]
    remove: List[str]


def build_response_rewrite(
        status_code: int,
        body: str,
        vars: Optional[str],
        body_base64: bool = False,
        headers: Optional[HeadersConfig] = None,
) -> Dict[str, str]:
    """generate response-rewrite plugin config

    Args:
        status_code (int): 修改上游返回状态码，默认保留原始响应代码。
        body (str):
            - 修改上游返回的 body 内容，如果设置了新内容，header 里面的 content-length 字段也会被去掉。
            - 注意，这个字段只允许对插件配置中传递的主体进行解码，并不对上游响应进行解码。
        vars (str, Optional):
            - vars 是一个表达式列表，只有满足条件的请求和响应才会修改 body 和 header 信息，来自 lua-resty-expr。
            - 如果 vars 字段为空，那么所有的重写动作都会被无条件的执行。
        body_base64 (bool, Optional): 当设置时，在写给客户端之前，在body中传递的主体将被解码，这在一些图像和 Protobuffer 场景中使用。
        headers (HeadersConfig, optional):
            - add (Dict[str, str]): 添加新的响应头。格式为 {"name": "value", ...}。这个值能够以 $var 的格式包含 NGINX 变量。
            - set (Dict[str, str]): 改写响应头。格式为 {"name": "value", ...}。这个值能够以 $var 的格式包含 NGINX 变量。
            - remove (List[str]): 移除响应头。格式为 ["name", ...]。

    Raises:
        ValueError: status_code must be between 200 and 598
        ValueError: key {} can not contain ':'

    Returns:
        {
            "type": "response-rewrite",
            "yaml": "body: ''\nbody_base64: false\nheaders:\n  add:\n  - key: key1:value1\n  remove:\n  - key: key1\n  set:\n  - key: key1\n    value: value1\nstatus_code: 200\nvars: ''\n"
        }
    """

    if not (200 <= status_code <= 598):
        raise ValueError("status_code must be between 200 and 598")

    if vars:
        _check_vars(vars, "response_rewrite")

    add_data = []
    for k, v in headers.add.items():
        if ":" in k:
            raise ValueError(f"key {k} can not contain ':'")
        add_data.append({"key": "{}: {}".format(k, v)})

    set_data = []
    for k, v in headers.set.items():
        if ":" in k:
            raise ValueError(f"key {k} can not contain ':'")
        set_data.append({"key": k, "value": v})

    remove_data = []
    for k in headers.remove:
        if ":" in k:
            raise ValueError(f"key {k} can not contain ':'")
        remove_data.append({"key": k})

    return {
        "type": "response-rewrite",
        "yaml": yaml_dump(
            {
                "status_code": status_code,
                "body_base64": body_base64,
                "body": body,
                "vars": vars,
                "headers": {
                    "add": add_data,
                    "set": set_data,
                    "remove": remove_data,
                }
            }
        ),
    }


def build_redirect(
    uri: str,
    ret_code: int = 302,
) -> Dict[str, str]:
    """generate redirect plugin config

    Args:
        uri (str): 要重定向到的 URI，可以包含 NGINX 变量。
        ret_code (int, Optional): HTTP 响应码。

    Raises:
        ValueError: ret_code cannot be less than 200

    Returns:
        {
            "type": "redirect",
            "yaml": "ret_code: 200\nuri: ''\n"
        }
    """

    if ret_code and ret_code < 200:
        raise ValueError("ret_code cannot be less than 200")

    return {
        "type": "redirect",
        "yaml": yaml_dump(
            {
                "uri": uri,
                "ret_code": ret_code,
            }
        ),
    }


def build_bk_access_token_source(
    source: str,
) -> Dict[str, str]:
    """generate bk-access-token-source plugin config

    Args:
        source (str): access_token 来源。Defaults to bearer.

    Raises:
        ValueError: source must be bearer or api_key

    Returns:
        {
            "type": "bk-access-token-source",
            "yaml": "source: bearer\n"
        }
    """

    if source not in ["bearer", "api_key"]:
        raise ValueError("source must be bearer or api_key.")

    return {
        "type": "bk-access-token-source",
        "yaml": yaml_dump(
            {
                "source": source,
            }
        ),
    }


def build_bk_username_required() -> Dict[str, str]:
    """generate bk-username-required plugin config

    Returns:
    {
        "type": "bk-username-required",
        "yaml": ""
    }
    """

    return {
        "type": "bk-username-required",
        "yaml": "",
    }


def _check_percentage(percentage: int, location: str):
    if percentage and not (0 < percentage <= 100):
        raise ValueError(f"The percentage of {location} must be greater than 0 and less than or equal to 100")


def _check_vars(vars: str, location: str):
    """check vars of lua-resty-expr
    vars = `[
        [
            [ "arg_name","==","jack" ],
            [ "arg_age","==",18 ]
        ],
        [
            [ "arg_name2","==111","allen" ]
        ]
    ]`

    """
    try:
        parsed_vars = ast.literal_eval(vars)
    except Exception as e:
        raise ValueError(f"The vars of {location} is not valid, error: {e}")

    # 第一层 parsed_vars = [ [a], [] ]
    if not isinstance(parsed_vars, list):
        raise TypeError(f"The vars of {location} should be list")

    for index, v in enumerate(parsed_vars):
        # 中间层  v = [a]
        if not isinstance(v, list):
            raise TypeError(f"The vars of {location} at index {index} should be list")

        for i, item in enumerate(v):
            # 最内侧 a  = [ "arg_name","==","jack" ]
            if isinstance(item, list):
                if len(item) != 3:
                    raise ValueError(f"The vars of {location} at index [{index}][{i}] should have 3 elements")
                if item[1] not in VARS_ALLOWED_COMPARISON_SYMBOLS:
                    raise ValueError(
                        f"The vars of {location} at index [{index}][{i}] should have a valid comparison symbol"
                    )
            else:
                raise TypeError(f"The vars of {location} at index [{index}][{i}] should be list")


def _validate_json_schema(schema_name: str, json_schema: str):
    try:
        data = json.loads(json_schema)
    except json.JSONDecodeError:
        raise ValueError(f"Your {schema_name} Schema is not a valid JSON")

    try:
        jsonschema.validate(instance=data, schema=Draft7Schema)
    except jsonschema.exceptions.ValidationError as err:
        raise ValueError(f"Your {schema_name} Schema is not valid: {err}")
