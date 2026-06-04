# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
this command will generate the resources.yaml from the drf_spectacular config of the apis under project

if only want part of the apis:
1. add the `tags` in `@extend_schema` of each method in the views.py
2. call this command with tag, e.g. `python manage.py generate_resource_yaml.py --tag=foo --tag=bar`

support manually configured routes via:
1. --extra-resource-file argument (can specify multiple files)
2. BK_APIGW_EXTRA_RESOURCE_FILES setting (list of file paths)
"""

from pathlib import Path
from typing import Dict, List

import yaml

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from drf_spectacular.management.commands.spectacular import SchemaValidationError
from drf_spectacular.renderers import OpenApiYamlRenderer
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.validation import validate_schema


def post_process_only_keep_the_apis_with_specified_tags(tags: List) -> callable:
    def only_keep_the_apis_with_specified_tags(result, generator, request, public):
        paths = result.get("paths", None)
        if not paths:
            return result

        api_to_delete = []
        for uri, methods in paths.items():
            for method, info in methods.items():
                if not set(tags).intersection(info.get("tags", [])):
                    api_to_delete.append((uri, method))

        for uri, method in api_to_delete:
            del paths[uri][method]

        result["paths"] = {k: v for k, v in paths.items() if v}
        return result

    return only_keep_the_apis_with_specified_tags


def post_process_inject_method_and_path(result, generator, request, public):
    paths = result.get("paths", None)
    if not paths:
        return result
    sub_path = settings.BK_APIGW_STAGE_BACKEND_SUBPATH

    for uri, methods in paths.items():
        for method, info in methods.items():
            info["x-bk-apigateway-resource"]["backend"]["method"] = method
            if not sub_path:
                info["x-bk-apigateway-resource"]["backend"]["path"] = uri
            else:
                info["x-bk-apigateway-resource"]["backend"]["path"] = f"{sub_path}{uri}"

    return result


def post_process_mcp_server_config(mcp_server_tools: list, delete_mcp_flag: bool) -> callable:
    """
    mcp_server_tools: 外部如果指定了mcp_server_tools，则只校验这些工具，如果没有，则校验所有开启了mcp server的工具
    """

    def get_mcp_server_tools(result, generator, request, public):
        paths = result.get("paths", None)
        if not paths:
            return result
        tool_set = set(mcp_server_tools)
        is_specified = len(tool_set) > 0
        # 可以被添加为mcp tool的工具
        mcp_can_used_tool = set()
        # 所有的资源
        all_resources = set()
        for uri, methods in paths.items():
            for method, info in methods.items():
                name = info.get("operationId")
                all_resources.add(name)
                if info.get("x-bk-apigateway-resource", None) and info["x-bk-apigateway-resource"].get("enableMcp",
                                                                                                       None):
                    # 生成 resource.yaml 的时候需要删除 enableMcp ，以防导入校验失败
                    if delete_mcp_flag:
                        del info["x-bk-apigateway-resource"]["enableMcp"]

                    # 如果 resource 不在指定的tool，则跳过
                    if name not in tool_set and is_specified:
                        continue
                    if info.get("parameters") or info.get("requestBody"):
                        # 如果没有指定工具，则自动将开启了mcp的资源添加进去
                        if not is_specified:
                            mcp_server_tools.append(name)
                        else:
                            mcp_can_used_tool.add(name)
                        continue
                    elif not info.get("noneSchema") and not info["x-bk-apigateway-resource"].get("noneSchema") :
                        raise Exception(f"mcp server tool:{name} need confirm api schema or if no schema and set "
                                        f"noneSchema=True")
                    else:
                        # 如果没有指定直接将符合的api以及开启了mcp的都加入到工具列表里面
                        if not is_specified:
                            mcp_server_tools.append(name)
                        else:
                            mcp_can_used_tool.add(name)
        # 如果指定了特定的工具，则需要校验指定的resoruce 是否在定义的资源里面以及是否符合要求
        if is_specified:
            for tool in tool_set:
                if tool not in all_resources:
                    raise Exception((f"mcp server tool:{tool} not found in resources.yaml"))
                if tool not in mcp_can_used_tool:
                    raise Exception(f"mcp server tool:{tool} "
                                    f"need confirm api schema or set noneSchema=True and enableMcp=True")

        return result

    return get_mcp_server_tools


def merge_extra_resources(schema: Dict, extra_resources_file: Path) -> Dict:
    """Load extra resources from a YAML file and merge into the schema.

    The extra resource file should follow the same OpenAPI 3.0 format as resources.yaml.
    Paths and components from the extra file will be merged into the schema.
    Raises an error on duplicate path+method combinations.
    """
    if not extra_resources_file.exists():
        raise CommandError(f"Extra resource file not found: {extra_resources_file}")

    with open(extra_resources_file, "r", encoding="utf-8") as f:
        extra = yaml.safe_load(f)

    if not isinstance(extra, dict):
        raise CommandError(f"Invalid extra resource file format: {extra_resources_file}")

    # Merge paths
    extra_paths = extra.get("paths", {})
    if extra_paths:
        existing_paths = schema.get("paths", {})
        for uri, methods in extra_paths.items():
            if not isinstance(methods, dict):
                raise CommandError(f"Invalid path definition for {uri} in {extra_resources_file}")
            if uri in existing_paths:
                for method in methods:
                    if method in existing_paths[uri]:
                        raise CommandError(
                            f"Duplicate path+method: {uri} {method} in {extra_resources_file}. "
                            f"This path+method already exists in the generated schema."
                        )
                existing_paths[uri].update(methods)
            else:
                existing_paths[uri] = methods
        schema["paths"] = existing_paths

    # Merge components (schemas, securitySchemes, etc.)
    extra_components = extra.get("components", {})
    if extra_components:
        existing_components = schema.get("components", {})
        for component_type, components in extra_components.items():
            if component_type not in existing_components:
                existing_components[component_type] = components
            else:
                for name, definition in components.items():
                    if name in existing_components[component_type]:
                        raise CommandError(
                            f"Duplicate component: {component_type}/{name} in {extra_resources_file}. "
                            f"This component already exists in the generated schema."
                        )
                    existing_components[component_type][name] = definition
        schema["components"] = existing_components

    return schema


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--tag",
            nargs="*",
            help="if set only generate the specified tags api to resources.yaml",
        )
        parser.add_argument(
            "--extra-resource-file",
            action="append",
            default=[],
            help="path to extra resource YAML file(s) to merge into generated resources.yaml "
            "(can specify multiple times)",
        )

    def handle(self, *args, **kwargs):
        define_dir = Path(settings.BASE_DIR)
        resources_path = define_dir / "resources.yaml"
        self.stdout.write(f"will generate {resources_path}")

        if hasattr(settings, "BK_APIGW_STAGE_ENABLE_MCP_SERVERS") and settings.BK_APIGW_STAGE_ENABLE_MCP_SERVERS:
            spectacular_settings.POSTPROCESSING_HOOKS.append(
                post_process_mcp_server_config([], delete_mcp_flag=True))
        tags = kwargs.get("tag")
        if tags:
            self.stdout.write(f"get tags, will only use the apis with tags: {tags}")
            spectacular_settings.POSTPROCESSING_HOOKS.append(post_process_only_keep_the_apis_with_specified_tags(tags))
        else:
            self.stdout.write("no argument --tag, will use all apis under the project")

        self.stdout.write(f"process the project sub_path={settings.BK_APIGW_STAGE_BACKEND_SUBPATH}")
        spectacular_settings.POSTPROCESSING_HOOKS.append(post_process_inject_method_and_path)

        generator = spectacular_settings.DEFAULT_GENERATOR_CLASS()
        renderer = OpenApiYamlRenderer()
        schema = generator.get_schema(request=None, public=True)

        # Merge extra resources from command argument and settings
        extra_resource_files = kwargs.get("extra_resource_file", [])
        if hasattr(settings, "BK_APIGW_EXTRA_RESOURCE_FILES"):
            extra_resource_files.extend(settings.BK_APIGW_EXTRA_RESOURCE_FILES)

        for extra_file in extra_resource_files:
            extra_path = Path(extra_file)
            # If relative path, resolve against BASE_DIR
            if not extra_path.is_absolute():
                extra_path = define_dir / extra_path

            self.stdout.write(f"merging extra resources from {extra_path}")
            schema = merge_extra_resources(schema, extra_path)

        self.stdout.write("validate schema of all apis")
        try:
            validate_schema(schema)
            self.stdout.write("schema validated")
        except Exception as e:
            self.stdout.write(f"schema validation failed: {str(e)}")
            raise SchemaValidationError(e)

        self.stdout.write(f"render resources.yaml to {resources_path}")
        output = renderer.render(schema, renderer_context={})
        with open(resources_path, "wb") as f:
            f.write(output)
