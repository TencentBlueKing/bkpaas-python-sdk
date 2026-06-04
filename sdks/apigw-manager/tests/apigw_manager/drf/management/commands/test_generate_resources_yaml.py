# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import argparse
from types import SimpleNamespace
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

from apigw_manager.drf.management.commands.generate_resources_yaml import (
    Command,
    SchemaValidationError,
    merge_extra_resources,
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


class TestMergeExtraResources:
    def test_merge_new_paths(self, tmp_path):
        extra_file = tmp_path / "extra.yaml"
        extra_file.write_text(yaml.dump({
            "paths": {
                "/api/v1/manual": {
                    "get": {
                        "operationId": "manual_get",
                        "tags": ["manual"],
                        "x-bk-apigateway-resource": {
                            "backend": {"name": "default", "method": "get", "path": "/api/v1/manual"},
                        },
                    }
                }
            }
        }))

        schema = {
            "openapi": "3.0.0",
            "paths": {
                "/api/v1/auto": {"get": {"operationId": "auto_get"}},
            },
        }
        result = merge_extra_resources(schema, extra_file)
        assert "/api/v1/auto" in result["paths"]
        assert "/api/v1/manual" in result["paths"]
        assert result["paths"]["/api/v1/manual"]["get"]["operationId"] == "manual_get"

    def test_merge_existing_path_new_method(self, tmp_path):
        extra_file = tmp_path / "extra.yaml"
        extra_file.write_text(yaml.dump({
            "paths": {
                "/api/v1/xxx": {
                    "post": {"operationId": "xxx_post"},
                }
            }
        }))

        schema = {
            "openapi": "3.0.0",
            "paths": {
                "/api/v1/xxx": {"get": {"operationId": "xxx_get"}},
            },
        }
        result = merge_extra_resources(schema, extra_file)
        assert "get" in result["paths"]["/api/v1/xxx"]
        assert "post" in result["paths"]["/api/v1/xxx"]

    def test_merge_raises_on_duplicate_path_method(self, tmp_path):
        extra_file = tmp_path / "extra.yaml"
        extra_file.write_text(yaml.dump({
            "paths": {
                "/api/v1/xxx": {
                    "get": {"operationId": "xxx_get_manual"},
                }
            }
        }))

        schema = {
            "openapi": "3.0.0",
            "paths": {
                "/api/v1/xxx": {"get": {"operationId": "xxx_get"}},
            },
        }
        with pytest.raises(Exception, match="Duplicate path\\+method"):
            merge_extra_resources(schema, extra_file)

    def test_merge_new_components(self, tmp_path):
        extra_file = tmp_path / "extra.yaml"
        extra_file.write_text(yaml.dump({
            "components": {
                "schemas": {
                    "ManualSchema": {"type": "object", "properties": {"id": {"type": "integer"}}},
                }
            }
        }))

        schema = {
            "openapi": "3.0.0",
            "components": {
                "schemas": {
                    "AutoSchema": {"type": "object"},
                }
            },
        }
        result = merge_extra_resources(schema, extra_file)
        assert "AutoSchema" in result["components"]["schemas"]
        assert "ManualSchema" in result["components"]["schemas"]

    def test_merge_raises_on_duplicate_component(self, tmp_path):
        extra_file = tmp_path / "extra.yaml"
        extra_file.write_text(yaml.dump({
            "components": {
                "schemas": {
                    "DuplicateSchema": {"type": "string"},
                }
            }
        }))

        schema = {
            "openapi": "3.0.0",
            "components": {
                "schemas": {
                    "DuplicateSchema": {"type": "object"},
                }
            },
        }
        with pytest.raises(Exception, match="Duplicate component"):
            merge_extra_resources(schema, extra_file)

    def test_merge_file_not_found(self, tmp_path):
        extra_file = tmp_path / "nonexistent.yaml"
        schema = {"openapi": "3.0.0"}
        with pytest.raises(Exception, match="Extra resource file not found"):
            merge_extra_resources(schema, extra_file)

    def test_merge_invalid_format(self, tmp_path):
        extra_file = tmp_path / "invalid.yaml"
        extra_file.write_text(yaml.dump(["not", "a", "dict"]))
        schema = {"openapi": "3.0.0"}
        with pytest.raises(Exception, match="Invalid extra resource file format"):
            merge_extra_resources(schema, extra_file)

    def test_merge_full_example(self, tmp_path):
        """Test merging a complete extra resource file similar to user's example."""
        extra_file = tmp_path / "extra.yaml"
        extra_content = """
paths:
  /api/v1/manual/{id}/:
    get:
      operationId: v1_manual
      description: This is a manually configured API
      parameters:
      - in: path
        name: id
        schema:
          type: integer
        required: true
      tags:
      - manual
      security:
      - ApiGatewayJWTAuthentication: []
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
          description: ''
      x-bk-apigateway-resource:
        isPublic: true
        matchSubpath: false
        backend:
          name: default
          method: get
          path: /api/v1/manual/{id}/
          matchSubpath: false
          timeout: 0
        allowApplyPermission: true
        authConfig:
          userVerifiedRequired: true
          appVerifiedRequired: true
          resourcePermissionRequired: true
components:
  securitySchemes:
    ApiGatewayJWTAuthentication:
      type: apiKey
      in: header
      name: X-BKAPI-JWT
"""
        extra_file.write_text(extra_content)

        schema = {
            "openapi": "3.0.3",
            "paths": {
                "/api/v1/demo/{id}/": {"get": {"operationId": "v1_demo"}},
            },
            "components": {"schemas": {}},
        }
        result = merge_extra_resources(schema, extra_file)
        assert "/api/v1/demo/{id}/" in result["paths"]
        assert "/api/v1/manual/{id}/" in result["paths"]
        assert "ApiGatewayJWTAuthentication" in result["components"]["securitySchemes"]


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
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.validate_schema")
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.spectacular_settings")
    def test_handle_with_extra_resource_file(
        self, mocked_spectacular_settings, mocked_validate_schema, mocked_renderer_cls, mocked_open, settings, tmp_path
    ):
        extra_file = tmp_path / "extra.yaml"
        extra_file.write_text(yaml.dump({
            "paths": {
                "/api/v1/manual": {"get": {"operationId": "manual_get"}},
            }
        }))

        settings.BASE_DIR = str(tmp_path)
        settings.BK_APIGW_STAGE_ENABLE_MCP_SERVERS = False
        settings.BK_APIGW_STAGE_BACKEND_SUBPATH = ""
        mocked_spectacular_settings.POSTPROCESSING_HOOKS = []

        generator = Mock()
        generator.get_schema.return_value = {
            "openapi": "3.0.0",
            "paths": {"/api/v1/auto": {"get": {"operationId": "auto_get"}}},
        }
        mocked_spectacular_settings.DEFAULT_GENERATOR_CLASS.return_value = generator

        renderer = Mock()
        renderer.render.return_value = b"rendered"
        mocked_renderer_cls.return_value = renderer

        # Patch merge_extra_resources to avoid file I/O
        with patch("apigw_manager.drf.management.commands.generate_resources_yaml.merge_extra_resources") as mocked_merge:
            merged_schema = {
                "openapi": "3.0.0",
                "paths": {
                    "/api/v1/auto": {"get": {"operationId": "auto_get"}},
                    "/api/v1/manual": {"get": {"operationId": "manual_get"}},
                },
            }
            mocked_merge.return_value = merged_schema

            command = Command()
            command.handle(extra_resource_file=[str(extra_file)])

            mocked_merge.assert_called_once()
            # Verify the schema passed to validate_schema includes merged paths
            validated_schema = mocked_validate_schema.call_args[0][0]
            assert "/api/v1/auto" in validated_schema["paths"]
            assert "/api/v1/manual" in validated_schema["paths"]

    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.open", new_callable=mock_open)
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.OpenApiYamlRenderer")
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.validate_schema")
    @patch("apigw_manager.drf.management.commands.generate_resources_yaml.spectacular_settings")
    def test_handle_with_extra_resource_file_from_settings(
        self, mocked_spectacular_settings, mocked_validate_schema, mocked_renderer_cls, mocked_open, settings, tmp_path
    ):
        extra_file = tmp_path / "extra.yaml"
        extra_file.write_text(yaml.dump({
            "paths": {
                "/api/v1/settings-manual": {"get": {"operationId": "settings_manual_get"}},
            }
        }))

        settings.BASE_DIR = str(tmp_path)
        settings.BK_APIGW_STAGE_ENABLE_MCP_SERVERS = False
        settings.BK_APIGW_STAGE_BACKEND_SUBPATH = ""
        settings.BK_APIGW_EXTRA_RESOURCE_FILES = [str(extra_file)]
        mocked_spectacular_settings.POSTPROCESSING_HOOKS = []

        generator = Mock()
        generator.get_schema.return_value = {"openapi": "3.0.0"}
        mocked_spectacular_settings.DEFAULT_GENERATOR_CLASS.return_value = generator

        renderer = Mock()
        renderer.render.return_value = b"rendered"
        mocked_renderer_cls.return_value = renderer

        # Patch merge_extra_resources to avoid file I/O
        with patch("apigw_manager.drf.management.commands.generate_resources_yaml.merge_extra_resources") as mocked_merge:
            merged_schema = {
                "openapi": "3.0.0",
                "paths": {
                    "/api/v1/settings-manual": {"get": {"operationId": "settings_manual_get"}},
                },
            }
            mocked_merge.return_value = merged_schema

            command = Command()
            command.handle()

            mocked_merge.assert_called_once()
            validated_schema = mocked_validate_schema.call_args[0][0]
            assert "/api/v1/settings-manual" in validated_schema["paths"]

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
