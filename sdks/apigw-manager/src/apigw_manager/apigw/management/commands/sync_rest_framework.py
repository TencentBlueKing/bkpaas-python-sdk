# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django REST Framework Sync Command

    自动同步在PaaS上部署的DRF项目api到网关

    1. 生成通用配置的definition.yaml
    2. 通过drf-spectacular生成的resources.yaml
    3. 执行相关同步命令, 网关名称默认用APP_CODE
    4. 如果配置的网关文档路径, 执行同步文档命令
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--api-name",
            type=str,
            default="",
            help="api name, if not set, use APP_CODE",
        )
        parser.add_argument(
            "--define-dir",
            type=str,
            default="support-files/apigateway",
            help="define file directory",
        )
        parser.add_argument(
            "--sync",
            type=bool,
            default=True,
            help="whether sync to gateway",
        )

    def handle(self, *args, **kwargs):
        gateway_name = (
            kwargs.get("api_name")
            or getattr(settings, "BK_APIGW_NAME")
            or os.environ.get("BKPAAS_APP_CODE")
        )
        if not gateway_name:
            self.stdout.write("api name is required")
            os.exit(1)

        define_dir = kwargs.get("define_dir")
        if not define_dir:
            self.stdout.write("define dir is required")
            os.exit(1)

        # 创建define path
        if not os.path.isdir(define_dir):
            self.stdout.write("create define dir: %s" % define_dir)
            os.makedirs(define_dir, exist_ok=True)

        # 创建definition.yaml
        self.stdout.write("create definition.yaml")
        definition_path = os.path.join(define_dir, "definition.yaml")
        with open(definition_path, "w", encoding="utf-8") as f:
            f.write(self.default_definition())

        # 创建resources.yaml
        self.stdout.write("create resources.yaml")
        resources_path = os.path.join(define_dir, "resources.yaml")

        call_command("spectacular", f"--file={resources_path}")

        if not kwargs.get("sync"):
            self.stdout.write("skip sync")
            return

        # 同步网关基本信息
        self.stdout.write("sync basic config")
        call_command(
            "sync_apigw_config",
            f"--gateway-name={gateway_name}",
            f"--file={definition_path}",
        )

        # 同步网关环境信息
        self.stdout.write("sync stage config")
        call_command(
            "sync_apigw_stage",
            f"--gateway-name={gateway_name}",
            f"--file={definition_path}",
        )

        # 同步网关资源
        self.stdout.write("sync resources")
        call_command(
            "sync_apigw_resources",
            f"--gateway-name={gateway_name}",
            "--delete",
            f"--file={resources_path}",
        )

        # 同步网关文档
        if getattr(settings, "BK_APIGW_RESOURCE_DOCS_BASE_DIR") or os.environ.get(
            "BK_APIGW_RESOURCE_DOCS_BASE_DIR"
        ):
            self.stdout.write("sync docs")
            call_command(
                "sync_resource_docs_by_archive",
                f"--gateway-name={gateway_name}",
                f"--file={definition_path}",
            )

        # 创建资源版本并发布
        self.stdout.write("create version and release")
        call_command(
            "create_version_and_release_apigw",
            f"--gateway-name={gateway_name}",
            f"--file={definition_path}",
            "--generate-sdks=true",
        )

    def default_definition(self):
        return """{% load apigw_extras %}
spec_version: 1

release:
  comment: "auto release the first version while installing"

apigateway:
  description: ""
  description_en: ""
  is_public: true
  maintainers:
    - "admin"

stage:
  name: "{{ environ.BKPAAS_ENVIRONMENT }}"
  proxy_http:
    timeout: 60
    upstreams:
      loadbalance: "roundrobin"
      hosts:
        - host: "{% url_from_env environ.BKPAAS_DEFAULT_PREALLOCATED_URLS environ.BKPAAS_ENVIRONMENT %}"
          weight: 100

{% if settings.BK_APIGW_RESOURCE_DOCS_BASE_DIR or environ.BK_APIGW_RESOURCE_DOCS_BASE_DIR %}
resource_docs:
  basedir: "{{ settings.BK_APIGW_RESOURCE_DOCS_BASE_DIR|default:environ.BK_APIGW_RESOURCE_DOCS_BASE_DIR }}"
{% endif %}"""
