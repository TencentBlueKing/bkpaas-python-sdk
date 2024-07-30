# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pytest
from apigw_manager.plugin.config import (
    build_bk_cors,
    build_bk_header_rewrite,
    build_bk_ip_restriction,
    build_bk_rate_limit,
    build_stage_plugin_config_for_definition_yaml,
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
