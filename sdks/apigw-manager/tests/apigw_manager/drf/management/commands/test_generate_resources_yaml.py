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

import argparse
from types import SimpleNamespace
from unittest.mock import Mock, mock_open, patch

import pytest

from apigw_manager.drf.management.commands.generate_resources_yaml import (
    Command,
    SchemaValidationError,
    post_process_inject_method_and_path,
    post_process_mcp_server_config,
    post_process_only_keep_the_apis_with_specified_tags,
)


@pytest.fixture()
def django_settings_subpath_empty(settings):
    settings.BK_APIGW_STAGE_BACKEND_SUBPATH = ""


@pytest.fixture()
def django_settings_subpath(settings):
    settings.BK_APIGW_STAGE_BACKEND_SUBPATH = "/mock"


class TestPostProcess:
    def test_only_keep_the_apis_with_specified_tags(self):
        tags = ["open"]

        f = post_process_only_keep_the_apis_with_specified_tags(tags)

        # no paths
        result1 = {"hello": "world"}
        data1 = f(result1, Mock(), Mock(), Mock())

        assert data1 == result1

        # with paths, no tag hit
        result2 = {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["close"]}},
            }
        }
        data2 = f(result2, Mock(), Mock(), Mock())
        assert data2 == {"paths": {}}

        # with paths, tag hit
        result3 = {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["open"]}, "post": {"tags": ["close"]}},
                "/api/v1/yyy": {"get": {"tags": ["close"]}, "post": {"tags": ["close"]}},
            }
        }
        data3 = f(result3, Mock(), Mock(), Mock())
        assert data3 == {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["open"]}},
            }
        }

    def test_post_process_inject_method_and_path_no_subpath(self, django_settings_subpath_empty):
        f = post_process_inject_method_and_path

        # no paths
        result1 = {"hello": "world"}
        data1 = f(result1, Mock(), Mock(), Mock())

        assert data1 == result1

        # with paths
        result2 = {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["open"], "x-bk-apigateway-resource": {"backend": {}}}},
            }
        }
        data2 = f(result2, Mock(), Mock(), Mock())
        assert data2 == {
            "paths": {
                "/api/v1/xxx": {
                    "get": {
                        "tags": ["open"],
                        "x-bk-apigateway-resource": {"backend": {"method": "get", "path": "/api/v1/xxx"}},
                    }
                },
            }
        }

    def test_post_process_inject_method_and_path_with_subpath(self, django_settings_subpath):
        f = post_process_inject_method_and_path

        # no paths
        result1 = {"hello": "world"}
        data1 = f(result1, Mock(), Mock(), Mock())

        assert data1 == result1

        # with paths
        result2 = {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["open"], "x-bk-apigateway-resource": {"backend": {}}}},
            }
        }
        data2 = f(result2, Mock(), Mock(), Mock())
        assert data2 == {
            "paths": {
                "/api/v1/xxx": {
                    "get": {
                        "tags": ["open"],
                        "x-bk-apigateway-resource": {"backend": {"method": "get", "path": "/mock/api/v1/xxx"}},
                    }
                },
            }
        }

    def test_post_process_mcp_server_config_no_paths(self):
        f = post_process_mcp_server_config([], delete_mcp_flag=True)
        result = {"hello": "world"}

        assert f(result, Mock(), Mock(), Mock()) == result

    def test_post_process_mcp_server_config_auto_collect_tools(self):
        mcp_server_tools = []
        f = post_process_mcp_server_config(mcp_server_tools, delete_mcp_flag=True)
        result = {
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

        data = f(result, Mock(), Mock(), Mock())

        assert mcp_server_tools == ["withParams", "noSchema"]
        assert data["paths"]["/api/v1/with-params"]["get"]["x-bk-apigateway-resource"] == {}
        assert data["paths"]["/api/v1/no-schema"]["post"]["x-bk-apigateway-resource"] == {"noneSchema": True}

    def test_post_process_mcp_server_config_raises_for_missing_schema(self):
        f = post_process_mcp_server_config([], delete_mcp_flag=False)
        result = {
            "paths": {
                "/api/v1/no-schema": {
                    "get": {
                        "operationId": "noSchema",
                        "x-bk-apigateway-resource": {"enableMcp": True},
                    }
                }
            }
        }

        with pytest.raises(Exception, match="noneSchema=True"):
            f(result, Mock(), Mock(), Mock())

    def test_post_process_mcp_server_config_accepts_specified_tool(self):
        f = post_process_mcp_server_config(["createThing"], delete_mcp_flag=False)
        result = {
            "paths": {
                "/api/v1/things": {
                    "post": {
                        "operationId": "createThing",
                        "requestBody": {"content": {}},
                        "x-bk-apigateway-resource": {"enableMcp": True},
                    }
                }
            }
        }

        assert f(result, Mock(), Mock(), Mock()) == result

    def test_post_process_mcp_server_config_accepts_specified_tool_with_none_schema(self):
        f = post_process_mcp_server_config(["noSchema"], delete_mcp_flag=False)
        result = {
            "paths": {
                "/api/v1/no-schema": {
                    "get": {
                        "operationId": "noSchema",
                        "x-bk-apigateway-resource": {"enableMcp": True, "noneSchema": True},
                    }
                }
            }
        }

        assert f(result, Mock(), Mock(), Mock()) == result

    def test_post_process_mcp_server_config_raises_for_unknown_specified_tool(self):
        f = post_process_mcp_server_config(["missingTool"], delete_mcp_flag=False)
        result = {
            "paths": {
                "/api/v1/things": {
                    "post": {
                        "operationId": "createThing",
                        "requestBody": {"content": {}},
                        "x-bk-apigateway-resource": {"enableMcp": True},
                    }
                }
            }
        }

        with pytest.raises(Exception, match="not found in resources.yaml"):
            f(result, Mock(), Mock(), Mock())

    def test_post_process_mcp_server_config_raises_for_invalid_specified_tool(self):
        f = post_process_mcp_server_config(["noSchema"], delete_mcp_flag=False)
        result = {
            "paths": {
                "/api/v1/no-schema": {
                    "get": {
                        "operationId": "noSchema",
                        "x-bk-apigateway-resource": {"enableMcp": True},
                    }
                }
            }
        }

        with pytest.raises(Exception, match="noneSchema=True"):
            f(result, Mock(), Mock(), Mock())

    def test_post_process_mcp_server_config_raises_for_non_mcp_specified_tool(self):
        f = post_process_mcp_server_config(["plainTool"], delete_mcp_flag=False)
        result = {
            "paths": {
                "/api/v1/plain": {
                    "get": {
                        "operationId": "plainTool",
                        "x-bk-apigateway-resource": {"noneSchema": True},
                    }
                }
            }
        }

        with pytest.raises(Exception, match="enableMcp=True"):
            f(result, Mock(), Mock(), Mock())


class TestCommand:
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.open", new_callable=mock_open)
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.OpenApiYamlRenderer")
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.validate_schema")
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.spectacular_settings")
    def test_handle(
        self, mocked_spectacular_settings, mocked_validate_schema, mocked_renderer_cls, mocked_open, settings, tmp_path
    ):
        settings.BASE_DIR = str(tmp_path)
        settings.BK_APIGW_STAGE_ENABLE_MCP_SERVERS = True
        settings.BK_APIGW_STAGE_BACKEND_SUBPATH = "/backend"
        mocked_spectacular_settings.POSTPROCESSING_HOOKS = []

        generator = Mock()
        generator.get_schema.return_value = {"openapi": "3.0.0"}
        mocked_spectacular_settings.DEFAULT_GENERATOR_CLASS.return_value = generator

        renderer = Mock()
        renderer.render.return_value = b"rendered"
        mocked_renderer_cls.return_value = renderer

        command = Command()
        parser = argparse.ArgumentParser()
        command.add_arguments(parser)

        assert parser.parse_args(["--tag", "public", "internal"]).tag == ["public", "internal"]

        command.handle(tag=["public"])

        mocked_validate_schema.assert_called_once_with({"openapi": "3.0.0"})
        renderer.render.assert_called_once_with({"openapi": "3.0.0"}, renderer_context={})
        mocked_open.assert_called_once_with(tmp_path / "resources.yaml", "wb")
        mocked_open().write.assert_called_once_with(b"rendered")
        assert len(mocked_spectacular_settings.POSTPROCESSING_HOOKS) == 3

    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.open", new_callable=mock_open)
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.OpenApiYamlRenderer")
    @patch(
        "apigw_manager.drf.management.commands.generate_resources_yaml.validate_schema", side_effect=Exception("boom")
    )
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.spectacular_settings")
    def test_handle_raises_schema_validation_error(
        self,
        mocked_spectacular_settings,
        mocked_validate_schema,
        mocked_renderer_cls,
        mocked_open,
        settings,
        tmp_path,
    ):
        settings.BASE_DIR = str(tmp_path)
        settings.BK_APIGW_STAGE_ENABLE_MCP_SERVERS = False
        settings.BK_APIGW_STAGE_BACKEND_SUBPATH = ""
        mocked_spectacular_settings.POSTPROCESSING_HOOKS = []

        generator = Mock()
        generator.get_schema.return_value = {"openapi": "3.0.0"}
        mocked_spectacular_settings.DEFAULT_GENERATOR_CLASS.return_value = generator
        mocked_renderer_cls.return_value = Mock()

        command = Command()

        with pytest.raises(SchemaValidationError, match="boom"):
            command.handle()

        mocked_validate_schema.assert_called_once_with({"openapi": "3.0.0"})
        mocked_open.assert_not_called()

    def test_handle_raises_without_base_dir(self):
        patched_settings = SimpleNamespace(BK_APIGW_STAGE_BACKEND_SUBPATH="")

        with patch("apigw_manager.drf.management.commands.generate_resources_yaml.settings", new=patched_settings):
            with pytest.raises(AttributeError, match="BASE_DIR"):
                Command().handle()

    def test_handle_raises_with_invalid_hooks(self, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_BACKEND_SUBPATH="",
        )
        patched_spectacular_settings = SimpleNamespace(
            POSTPROCESSING_HOOKS=object(),
            DEFAULT_GENERATOR_CLASS=lambda: Mock(),
        )

        with patch("apigw_manager.drf.management.commands.generate_resources_yaml.settings", new=patched_settings):
            with patch(
                "apigw_manager.drf.management.commands.generate_resources_yaml.spectacular_settings",
                new=patched_spectacular_settings,
            ):
                with pytest.raises(AttributeError, match="append"):
                    Command().handle()

    def test_handle_raises_with_invalid_generator_class(self, tmp_path):
        patched_settings = SimpleNamespace(
            BASE_DIR=str(tmp_path),
            BK_APIGW_STAGE_BACKEND_SUBPATH="",
        )
        patched_spectacular_settings = SimpleNamespace(
            POSTPROCESSING_HOOKS=[],
            DEFAULT_GENERATOR_CLASS=None,
        )

        with patch("apigw_manager.drf.management.commands.generate_resources_yaml.settings", new=patched_settings):
            with patch(
                "apigw_manager.drf.management.commands.generate_resources_yaml.spectacular_settings",
                new=patched_spectacular_settings,
            ):
                with pytest.raises(TypeError, match="NoneType.*callable"):
                    Command().handle()
