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

from types import SimpleNamespace
from unittest.mock import Mock, mock_open, patch

import pytest
from django.core.management.base import CommandError

from apigw_manager.drf.management.commands.generate_definition_yaml import Command


class AppendOnlyHooks:
    def __init__(self):
        self.values = []

    def append(self, value):
        self.values.append(value)


class TestCommand:
    @patch("apigw_manager.drf.management.commands.generate_definition_yaml.shutil.copyfile")
    def test_handle_copies_template_without_render(self, mocked_copyfile, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_ENABLE_MCP_SERVERS=False,
        )

        with patch("apigw_manager.drf.management.commands.generate_definition_yaml.settings", new=patched_settings):
            Command().handle(render=False)

        mocked_copyfile.assert_called_once()
        assert mocked_copyfile.call_args.args[1] == tmp_path / "definition.yaml"

    @patch("apigw_manager.drf.management.commands.generate_definition_yaml.open", new_callable=mock_open)
    def test_handle_renders_template(self, mocked_open, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_ENABLE_MCP_SERVERS=False,
            BK_APIGW_RELEASE_VERSION="1.0.0",
        )
        mocked_open.return_value.read.return_value = "version: {{ settings.BK_APIGW_RELEASE_VERSION }}\n\n"

        with patch("apigw_manager.drf.management.commands.generate_definition_yaml.settings", new=patched_settings):
            Command().handle(render=True)

        mocked_open.assert_any_call(tmp_path / "definition.yaml", "w")
        mocked_open().write.assert_called_once_with("version: 1.0.0")

    @patch("apigw_manager.drf.management.commands.generate_definition_yaml.shutil.copyfile")
    @patch("apigw_manager.drf.management.commands.generate_definition_yaml.OpenApiYamlRenderer")
    def test_handle_fills_mcp_server_tools(self, mocked_renderer_cls, mocked_copyfile, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_ENABLE_MCP_SERVERS=True,
            BK_APIGW_STAGE_MCP_SERVERS=[{"tools": []}],
        )
        patched_spectacular_settings = SimpleNamespace(POSTPROCESSING_HOOKS=[], DEFAULT_GENERATOR_CLASS=None)

        class HookRunningGenerator:
            def get_schema(self, request, public):
                schema = {
                    "paths": {
                        "/api/v1/with-params": {
                            "get": {
                                "operationId": "withParams",
                                "parameters": [{"name": "id"}],
                                "x-bk-apigateway-resource": {"enableMcp": True},
                            }
                        },
                        "/api/v1/no-schema": {
                            "post": {
                                "operationId": "noSchema",
                                "x-bk-apigateway-resource": {"enableMcp": True, "noneSchema": True},
                            }
                        },
                    }
                }
                for hook in patched_spectacular_settings.POSTPROCESSING_HOOKS:
                    schema = hook(schema, self, request, public)
                return schema

        patched_spectacular_settings.DEFAULT_GENERATOR_CLASS = HookRunningGenerator
        mocked_renderer_cls.return_value = Mock()

        with patch("apigw_manager.drf.management.commands.generate_definition_yaml.settings", new=patched_settings):
            with patch(
                "apigw_manager.drf.management.commands.generate_definition_yaml.spectacular_settings",
                new=patched_spectacular_settings,
            ):
                Command().handle(render=False)

        assert patched_settings.BK_APIGW_STAGE_MCP_SERVERS[0]["tools"] == ["withParams", "noSchema"]
        mocked_copyfile.assert_called_once()
        mocked_renderer_cls.return_value.render.assert_called_once()

    def test_handle_raises_command_error_without_mcp_servers(self, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_ENABLE_MCP_SERVERS=True,
        )
        patched_spectacular_settings = SimpleNamespace(
            POSTPROCESSING_HOOKS=[],
            DEFAULT_GENERATOR_CLASS=lambda: Mock(),
        )

        with patch("apigw_manager.drf.management.commands.generate_definition_yaml.settings", new=patched_settings):
            with patch(
                "apigw_manager.drf.management.commands.generate_definition_yaml.spectacular_settings",
                new=patched_spectacular_settings,
            ):
                with pytest.raises(CommandError, match="BK_APIGW_STAGE_MCP_SERVERS"):
                    Command().handle(render=False)

    def test_handle_raises_command_error_with_invalid_mcp_server_tools(self, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_ENABLE_MCP_SERVERS=True,
            BK_APIGW_STAGE_MCP_SERVERS=[{"tools": "not-a-list"}],
        )
        patched_spectacular_settings = SimpleNamespace(
            POSTPROCESSING_HOOKS=[],
            DEFAULT_GENERATOR_CLASS=lambda: Mock(),
        )

        with patch("apigw_manager.drf.management.commands.generate_definition_yaml.settings", new=patched_settings):
            with patch(
                "apigw_manager.drf.management.commands.generate_definition_yaml.spectacular_settings",
                new=patched_spectacular_settings,
            ):
                with pytest.raises(CommandError, match=r"\['tools'\] must be a list"):
                    Command().handle(render=False)

    def test_handle_raises_command_error_with_invalid_mcp_server_item(self, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_ENABLE_MCP_SERVERS=True,
            BK_APIGW_STAGE_MCP_SERVERS=["not-a-dict"],
        )
        patched_spectacular_settings = SimpleNamespace(
            POSTPROCESSING_HOOKS=[],
            DEFAULT_GENERATOR_CLASS=lambda: Mock(),
        )

        with patch("apigw_manager.drf.management.commands.generate_definition_yaml.settings", new=patched_settings):
            with patch(
                "apigw_manager.drf.management.commands.generate_definition_yaml.spectacular_settings",
                new=patched_spectacular_settings,
            ):
                with pytest.raises(CommandError, match="items must be dict-like"):
                    Command().handle(render=False)

    def test_handle_raises_command_error_with_invalid_hooks(self, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_ENABLE_MCP_SERVERS=True,
            BK_APIGW_STAGE_MCP_SERVERS=[{}],
        )
        patched_spectacular_settings = SimpleNamespace(
            POSTPROCESSING_HOOKS=AppendOnlyHooks(),
            DEFAULT_GENERATOR_CLASS=lambda: Mock(),
        )

        with patch("apigw_manager.drf.management.commands.generate_definition_yaml.settings", new=patched_settings):
            with patch(
                "apigw_manager.drf.management.commands.generate_definition_yaml.spectacular_settings",
                new=patched_spectacular_settings,
            ):
                with pytest.raises(CommandError, match=r"clear\(\)"):
                    Command().handle(render=False)

    def test_handle_raises_command_error_with_invalid_generator_class(self, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_ENABLE_MCP_SERVERS=True,
            BK_APIGW_STAGE_MCP_SERVERS=[{}],
        )
        patched_spectacular_settings = SimpleNamespace(
            POSTPROCESSING_HOOKS=[],
            DEFAULT_GENERATOR_CLASS=None,
        )

        with patch("apigw_manager.drf.management.commands.generate_definition_yaml.settings", new=patched_settings):
            with patch(
                "apigw_manager.drf.management.commands.generate_definition_yaml.spectacular_settings",
                new=patched_spectacular_settings,
            ):
                with pytest.raises(CommandError, match="DEFAULT_GENERATOR_CLASS"):
                    Command().handle(render=False)
