# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
import json

import pytest
from apigw_manager.plugin.config import (
    build_bk_cors,
    build_bk_header_rewrite,
    build_bk_ip_restriction,
    build_bk_rate_limit,
    build_bk_mock,
    build_api_breaker,
    build_fault_injection,
    build_request_validation,
    build_stage_plugin_config_for_definition_yaml,
    UnhealthyConfig,
    HealthyConfig,
    AbortConfig,
    DelayConfig,
    validate_json_schema,
)


class TestBuildPluginConfig:
    @pytest.mark.parametrize(
        "set, remove, will_error, expected",
        [
            (
                {"key1": "value1", "key2": "value2"},
                ["key1"],
                False,
                {
                    "type": "bk-header-rewrite",
                    "yaml": "remove:\n- key: key1\nset:\n- key: key1\n  value: value1\n- key: key2\n  value: value2\n",
                },
            ),
            (
                {"key:1": "value1", "key2": "value2"},
                ["key1"],
                True,
                None,
            ),
            (
                {"key1": "value1", "key2": "value2"},
                ["key:1"],
                True,
                None,
            ),
        ],
    )
    def test_build_bk_header_rewrite(self, set, remove, will_error, expected):
        if will_error:
            with pytest.raises(ValueError):
                build_bk_header_rewrite(set, remove)
            return

        assert build_bk_header_rewrite(set, remove) == expected

    @pytest.mark.parametrize(
        "data, will_error, expected",
        [
            (
                {},
                False,
                {
                    "type": "bk-cors",
                    "yaml": "allow_credential: false\n"
                    "allow_headers: '*'\n"
                    "allow_methods: '*'\n"
                    "allow_origins: '*'\n"
                    "allow_origins_by_regex: null\n"
                    "expose_headers: '*'\n"
                    "max_age: 86400\n",
                },
            ),
            ({"allow_credential": True, "allow_origins": "*"}, True, None),
            ({"allow_credential": True, "allow_methods": "*"}, True, None),
            ({"allow_credential": True, "allow_headers": "*"}, True, None),
            # allow origins and allow_origins_by_regex
            ({"allow_origins": "*", "allow_origins_by_regex": "*"}, True, None),
            ({"allow_methods": "NOT_VALID"}, True, None),
        ],
    )
    def test_build_bk_cors(self, data, will_error, expected):
        if will_error:
            with pytest.raises(ValueError):
                build_bk_cors(**data)
            return

        assert build_bk_cors(**data) == expected

    @pytest.mark.parametrize(
        "whitelist, blacklist, will_error, expected",
        [
            (
                ["127.0.0.1"],
                None,
                False,
                {"type": "bk-ip-restriction", "yaml": "whitelist: |-\n  127.0.0.1\n"},
            ),
            (
                ["127.0.0.1/8"],
                None,
                False,
                {"type": "bk-ip-restriction", "yaml": "whitelist: |-\n  127.0.0.1/8\n"},
            ),
            (
                None,
                ["127.0.0.1"],
                False,
                {"type": "bk-ip-restriction", "yaml": "blacklist: |-\n  127.0.0.1\n"},
            ),
            (
                ["127.0.0.1"],
                ["127.0.0.1"],
                True,
                None,
            ),
            (
                None,
                None,
                True,
                None,
            ),
            (
                ["invalid_ip"],
                None,
                True,
                None,
            ),
        ],
    )
    def test_build_bk_ip_restriction(self, whitelist, blacklist, will_error, expected):
        if will_error:
            with pytest.raises(ValueError):
                build_bk_ip_restriction(whitelist, blacklist)
            return

        assert build_bk_ip_restriction(whitelist, blacklist) == expected

    @pytest.mark.parametrize(
        "default_period, default_tokens, specific_app_limits, will_error, expected",
        [
            (
                1,
                1000,
                [("demo", 60, 1000)],
                False,
                {
                    "type": "bk-rate-limit",
                    "yaml": "rates:\n"
                    "  __default:\n"
                    "  - period: 1\n"
                    "    tokens: 1000\n"
                    "  demo:\n"
                    "  - period: 60\n"
                    "    tokens: 1000\n",
                },
            ),
            (
                20,
                1000,
                None,
                True,
                None,
            ),
            (
                1,
                1000,
                [("demo", 20, 1000)],
                True,
                None,
            ),
        ],
    )
    def test_build_bk_rate_limit(self, default_period, default_tokens, specific_app_limits, will_error, expected):
        if will_error:
            with pytest.raises(ValueError):
                build_bk_rate_limit(default_period, default_tokens, specific_app_limits)
            return

        assert build_bk_rate_limit(default_period, default_tokens, specific_app_limits) == expected

    @pytest.mark.parametrize(
        "response_example, response_headers, response_status, will_error, expected",
        [
            (
                "",
                {"key1": "value1", "key2": "value2"},
                200,
                False,
                {
                    "type": "bk-mock",
                    "yaml": "response_example: ''\n"
                    "response_headers:\n"
                    "- key: key1\n"
                    "  value: value1\n"
                    "- key: key2\n"
                    "  value: value2\n"
                    "response_status: 200\n",
                },
            ),
            (
                "",
                {"key1": "value1", "key2": "value2"},
                99,
                True,
                None,
            ),
            (
                "",
                {"key:1": "value1", "key2": "value2"},
                200,
                True,
                None,
            ),
        ],
    )
    def test_build_bk_mock(self, response_example, response_headers, response_status, will_error, expected):
        if will_error:
            with pytest.raises(ValueError):
                build_bk_mock(response_example, response_headers, response_status)
            return

        assert build_bk_mock(response_example, response_headers, response_status) == expected

    @pytest.mark.parametrize(
        "break_response_body, break_response_headers, unhealthy, healthy,"
        "break_response_code, max_breaker_sec, will_error, expected",
        [
            (
                "",
                {"key1": "value1"},
                UnhealthyConfig(http_statuses=[503], failures=3),
                HealthyConfig(http_statuses=[200], successes=3),
                503,
                30,
                False,
                {
                    "type": "api-breaker",
                    "yaml": "break_response_body: ''\n"
                    "break_response_code: 503\n"
                    "break_response_headers:\n"
                    "- key: key1\n"
                    "  value: value1\n"
                    "healthy:\n"
                    "  http_statuses:\n"
                    "  - 200\n"
                    "  successes: 3\n"
                    "max_breaker_sec: 30\n"
                    "unhealthy:\n"
                    "  failures: 3\n"
                    "  http_statuses:\n"
                    "  - 503\n",
                },
            ),
            (
                "",
                {},
                UnhealthyConfig(http_statuses=[503], failures=1),
                HealthyConfig(http_statuses=[200], successes=1),
                502,
                2,
                True,
                None,
            ),
            (
                "",
                {},
                UnhealthyConfig(http_statuses=[400], failures=1),
                HealthyConfig(),
                502,
                300,
                True,
                None,
            ),
            (
                "",
                {},
                UnhealthyConfig(http_statuses=[503], failures=0),
                HealthyConfig(),
                502,
                300,
                True,
                None,
            ),
            (
                "",
                {},
                UnhealthyConfig(),
                HealthyConfig(http_statuses=[100], successes=1),
                502,
                300,
                True,
                None,
            ),
            (
                "",
                {},
                UnhealthyConfig(),
                HealthyConfig(http_statuses=[200], successes=0),
                502,
                300,
                True,
                None,
            ),
            (
                "",
                {"key:1": "value1"},
                UnhealthyConfig(http_statuses=[503], failures=1),
                HealthyConfig(http_statuses=[200], successes=1),
                502,
                300,
                True,
                None,
            ),
        ],
    )
    def test_build_api_breaker(
        self,
        break_response_body,
        break_response_headers,
        unhealthy,
        healthy,
        break_response_code,
        max_breaker_sec,
        will_error,
        expected,
    ):
        if will_error:
            with pytest.raises(ValueError):
                build_api_breaker(
                    break_response_body,
                    break_response_headers,
                    unhealthy,
                    healthy,
                    break_response_code,
                    max_breaker_sec,
                )
            return

        assert (
            build_api_breaker(
                break_response_body, break_response_headers, unhealthy, healthy, break_response_code, max_breaker_sec
            )
            == expected
        )

    @pytest.mark.parametrize(
        "abort, delay, will_error, expected",
        [
            (
                AbortConfig(http_status=503, body="test", percentage=50, vars=""),
                None,
                False,
                {
                    "type": "fault-injection",
                    "yaml": "abort:\n  body: test\n  http_status: 503\n  percentage: 50\n  vars: ''\n"
                },
            ),
            (
                None,
                DelayConfig(duration=3, percentage=30, vars=""),
                False,
                {
                    "type": "fault-injection",
                    "yaml": "delay:\n  duration: 3\n  percentage: 30\n  vars: ''\n"
                },
            ),
            (
                AbortConfig(http_status=500, body="", percentage=20, vars=""),
                DelayConfig(duration=2.5, percentage=100, vars=""),
                False,
                {
                    "type": "fault-injection",
                    "yaml": "abort:\n  body: ''\n  http_status: 500\n  percentage: 20\n  vars: ''\ndelay:\n  duration: 2.5\n  percentage: 100\n  vars: ''\n"
                },
            ),
            (
                AbortConfig(http_status=500, body="", percentage=20, vars=""),
                DelayConfig(duration=1, percentage=101, vars=""),
                True,
                None,
            ),
            (
                AbortConfig(http_status=500, body="", percentage=20, vars=""),
                DelayConfig(duration=1, percentage=101, vars=""),
                True,
                None,
            ),
            (
                None,
                DelayConfig(duration=1, percentage=-1, vars=""),
                True,
                None,
            ),
            (
                None,
                None,
                True,
                None
            ),
        ],
    )
    def test_build_fault_injection_config(self, abort, delay, will_error, expected):
        if will_error:
            with pytest.raises(ValueError):
                build_fault_injection(abort, delay)
            return

        assert build_fault_injection(abort, delay) == expected

    @pytest.mark.parametrize(
        "body_schema, header_schema, rejected_msg, rejected_code, will_error, expected",
        [
            (
                json.dumps({"type": "object"}),
                "",
                "test",
                403,
                False,
                {
                    "type": "request-validation",
                    "yaml": 'body_schema: \'{"type": "object"}\'\nrejected_code: 403\nrejected_msg: test\n'
                },
            ),
            (
                "",
                json.dumps({"type": "object"}),
                "test",
                403,
                False,
                {
                    "type": "request-validation",
                    "yaml": 'header_schema: \'{"type": "object"}\'\nrejected_code: 403\nrejected_msg: test\n'
                },
            ),
            (
                json.dumps({"type": "object"}),
                json.dumps({"type": "object"}),
                "test",
                403,
                False,
                {
                    "type": "request-validation",
                    "yaml": 'body_schema: \'{"type": "object"}\'\nheader_schema: \'{"type": "object"}\'\nrejected_code: 403\nrejected_msg: test\n'
                },
            ),
            (
                json.dumps({"type": "object"}),
                "",
                "test",
                199,
                True,
                None,
            ),
            (
                "",
                "",
                "test",
                403,
                True,
                None,
            ),
        ]
    )
    def test_build_request_validation(
        self, body_schema, header_schema, rejected_msg, rejected_code, will_error, expected
    ):
        if will_error:
            with pytest.raises(ValueError):
                build_request_validation(body_schema, header_schema, rejected_msg, rejected_code)
            return

        assert build_request_validation(body_schema, header_schema, rejected_msg, rejected_code) == expected


class TestBuildStagePluginConfigForDefinitionYaml:
    def test_build_stage_plugin_config_for_definition_yaml(self):
        yaml_str = """a
b
c"""
        plugin_configs = [{"type": "bk-rate-limit", "yaml": yaml_str}]
        result = build_stage_plugin_config_for_definition_yaml(plugin_configs, indent=2)

        expected_yaml_str = """a
  b
  c"""

        assert result == [{"type": "bk-rate-limit", "yaml": expected_yaml_str}]
