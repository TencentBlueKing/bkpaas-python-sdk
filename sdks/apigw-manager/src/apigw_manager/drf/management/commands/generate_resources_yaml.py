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
"""

from pathlib import Path
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand
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


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--tag",
            nargs="*",
            help="if set only generate the specified tags api to resources.yaml",
        )

    def handle(self, *args, **kwargs):
        define_dir = Path(settings.BASE_DIR)
        resources_path = define_dir / "resources.yaml"
        self.stdout.write(f"will generate {resources_path}")

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
