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
from datetime import datetime

from packaging.version import InvalidVersion

from apigw_manager.apigw.command import DefinitionCommand
from apigw_manager.apigw.helper import ResourceSignatureManager
from apigw_manager.apigw.utils import parse_version
from apigw_manager.core.fetch import Fetcher
from apigw_manager.core.release import Releaser


class Command(DefinitionCommand):
    """API gateway release a version"""

    default_namespace = "release"
    Fetcher = Fetcher
    Releaser = Releaser
    ResourceSignatureManager = ResourceSignatureManager
    now_func = datetime.now

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument("-t", "--title", default=None, help="release title")
        parser.add_argument("-c", "--comment", default="", help="release comment")
        parser.add_argument("-s", "--stage", default=[], nargs="+", help="release stages")
        parser.add_argument("--generate-sdks", default=False, action="store_true", help="with sdks generation")

    def _parse_version_from_definition(self, definition):
        version = definition.get("version")
        if not version:
            return None

        return parse_version(version)

    def _parse_version_from_resource_version(self, resource_version):
        version = resource_version and resource_version.get("version")
        if not version:
            return None

        try:
            return parse_version(version)
        except InvalidVersion:
            return None

    def _fix_defined_version(self, defined_version):
        if defined_version is None:
            return parse_version("0.0.1")

        return defined_version

    def _should_create_resource_version(self, manager, gateway_name, defined_version, latest_version):
        # 版本一致，且没有变更
        if latest_version and defined_version.public == latest_version.public and not manager.is_dirty(gateway_name):
            return False
        return True

    def _get_version_to_be_created(self, defined_version, resource_version_exists):
        if resource_version_exists:
            now_str = self.now_func().strftime("%Y%m%d%H%M%S")
            return parse_version("%s+%s" % (defined_version.public, now_str))

        return defined_version

    def _create_resource_version(self, releaser, version, title, comment):
        return releaser.create_resource_version(
            version=str(version),
            title=title,
            comment=comment,
        )

    def _check_resource_version_exists(self, fetcher, version):
        resource_versions = fetcher.list_resource_versions(version=str(version))
        return resource_versions["count"] != 0

    def _generate_sdks(self, releaser, version, *args, **kwargs):
        try:
            releaser.generate_sdks(resource_version=version)
        except Exception as err:
            print("warning!! generate sdks failed: %s" % err)

    def handle(self, stage, title, comment, generate_sdks, *args, **kwargs):
        configuration = self.get_configuration(**kwargs)
        definition = self.get_definition(**kwargs)
        defined_version = self._parse_version_from_definition(definition)
        fixed_defined_version = self._fix_defined_version(defined_version)

        fetcher = self.Fetcher(configuration)
        resource_version = fetcher.latest_resource_version()
        latest_version = self._parse_version_from_resource_version(resource_version)

        releaser = self.Releaser(configuration)
        manager = self.ResourceSignatureManager()
        gateway_name = configuration.gateway_name

        # 如何判断是否需要创建新版本？
        # 1. 使用配置中的版本号与线上最新版本进行比较，如果版本 public 部分不一致，则需要创建新版本
        # 2. 如果配置中的版本号与线上最新版本 public 部分一致，为了避免开发者忘记更新版本号的情况，获取同步结果进行判断：
        #    - 如果有资源变更，则需要创建新版本
        if self._should_create_resource_version(manager, gateway_name, fixed_defined_version, latest_version):
            exists = self._check_resource_version_exists(fetcher, fixed_defined_version)
            resource_version = self._create_resource_version(
                releaser=releaser,
                version=self._get_version_to_be_created(fixed_defined_version, exists),
                title=title or definition.get("title", ""),
                comment=comment or definition.get("comment", ""),
            )
            manager.reset_dirty(gateway_name)

        else:
            generate_sdks = False
            print("resource_version %s already exists, skip creating" % latest_version)

        result = releaser.release(
            version=resource_version["version"],
            title=title or resource_version.get("title", ""),
            comment=comment or resource_version.get("comment", ""),
            stage_names=stage,
        )
        print(
            "API gateway released %s, title %s, stages %s"
            % (result.get("version"), result["resource_version_title"], result["stage_names"])
        )

        # create a sdk when released a new version
        if generate_sdks:
            self._generate_sdks(
                releaser,
                resource_version["version"],
                *args,
                **kwargs,
            )
