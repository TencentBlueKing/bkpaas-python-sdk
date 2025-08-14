# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
this command will generate the definition.yaml

it will copy a template definition.yaml from apigw_manager into the project. And if the version of apigw_manager changes,
the template definition.yaml will be updated.
"""
import re
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template import Template, Context, context
from django.template.loader import render_to_string
from drf_spectacular.renderers import OpenApiYamlRenderer
from drf_spectacular.settings import spectacular_settings
from pathlib import Path

from apigw_manager.drf.management.commands.generate_resources_yaml import post_process_mcp_server_config


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--render",
            default=False,
            action="store_true",
            help="render definition.yaml",
        )


    def handle(self, *args, **kwargs):
        render = kwargs.get("render")
        # 构建动态配置上下文
        current_dir = Path(__file__).resolve().parent
        source_file = current_dir / "data" / "definition.yaml"

        define_dir = Path(settings.BASE_DIR)
        definition_path = define_dir / "definition.yaml"

        self.stdout.write(f"will generate {definition_path} from {source_file}")
        # 如果启用了MCP服务器，则需要生成 mcp_servers 配置
        if hasattr(settings, "BK_APIGW_STAGE_ENABLE_MCP_SERVERS") and settings.BK_APIGW_STAGE_ENABLE_MCP_SERVERS:
            for mcp_server in settings.BK_APIGW_STAGE_MCP_SERVERS:
                mcp_server_tools = mcp_server.get("tools", [])
                spectacular_settings.POSTPROCESSING_HOOKS.clear()
                spectacular_settings.POSTPROCESSING_HOOKS.append(
                    post_process_mcp_server_config(mcp_server_tools, delete_mcp_flag=False))
                generator = spectacular_settings.DEFAULT_GENERATOR_CLASS()
                renderer = OpenApiYamlRenderer()
                schema = generator.get_schema(request=None, public=True)
                renderer.render(schema, renderer_context={})
                mcp_server["tools"] = mcp_server_tools
        if render:
            with open(source_file) as f:
                template = Template(f.read())
                rendered = render_to_string(template, Context(context))
                cleaned = re.sub(r'\n\s*\n', '\n', rendered).strip()
                self.stdout.write(cleaned)
            with open(definition_path, 'w') as f:
                f.write(cleaned)

        else:
            shutil.copyfile(source_file, definition_path)
        self.stdout.write(f"generated {definition_path} from {source_file} success")
