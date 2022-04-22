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

from apigw_manager.apigw.command import DefinitionCommand
from apigw_manager.apigw.helper import ResourceSignatureManager
from apigw_manager.core.fetch import Fetcher
from apigw_manager.core.release import Releaser
from packaging.version import LegacyVersion
from packaging.version import parse as parse_version


class Command(DefinitionCommand):
    """API gateway release a version"""

    # 如何判断是否需要创建新版本？
    # 1.使用配置中的版本号与线上版本进行比较，如果不一致，直接使用配置中的版本号创建新版本
    # 2.如果配置中的版本号与线上版本一致，为了避免开发者忘记更新版本号的情况，获取同步结果进行判断：
    #   - 如果有资源变更，使用配置中的版本号（加上当前时间作为元数据）创建新版本

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

    def get_version_from_definition(self, definition):
        version = definition.get("version")
        if version:
            return parse_version(version)
        return None

    def get_version_from_resource_version(self, resource_version):
        if not resource_version:
            return None

        version = resource_version.get("version")
        if version:
            return parse_version(version)
        return None

    def fix_version(self, current_version, latest_version):
        if isinstance(current_version, LegacyVersion):
            raise ValueError("current version %s is not a valid version" % current_version)

        # 非语义化版本，直接忽略
        if isinstance(latest_version, LegacyVersion):
            latest_version = None

        # 没有发布记录且没配置版本
        if current_version is None and latest_version is None:
            return parse_version("0.0.1"), parse_version("?")

        # 没有发布过
        if latest_version is None:
            return current_version, parse_version("?")

        now_str = self.now_func().strftime("%Y%m%d%H%M%S")
        # 没有配置版本
        if current_version is None:
            # 加上当前时间作为元数据，但不改变版本优先级
            current_version = parse_version("%s+%s" % (latest_version.public, now_str))
        # 手动升级过线上版本，或者同一版本已发布过，但版本内容发生了变化，需要重新发布
        elif current_version <= latest_version:
            current_version = parse_version("%s+%s" % (current_version.public, now_str))

        return current_version, latest_version

    def should_create_resource_version(self, manager, api_name, current_version, latest_version):
        # 版本一致，且没有变更
        if current_version.public == latest_version.public and not manager.is_dirty(api_name):
            return False
        return True

    def create_resource_version(
        self,
        releaser,
        current_version,
        title,
        comment,
    ):

        version = str(current_version)
        resource_version = releaser.create_resource_version(
            version=version,
            title=title,
            comment=comment,
        )

        return resource_version

    def generate_sdks(self, releaser, resource_version, generate_sdks, *args, **kwargs):
        if not generate_sdks:
            return

        releaser.generate_sdks(resource_version=resource_version["version"])

    def handle(self, stage, title, comment, *args, **kwargs):
        configuration = self.get_configuration(**kwargs)
        definition = self.get_definition(**kwargs)
        current_version = self.get_version_from_definition(definition)

        fetcher = self.Fetcher(configuration)
        resource_version = fetcher.latest_resource_version()
        latest_version = self.get_version_from_resource_version(resource_version)

        current_version, latest_version = self.fix_version(current_version, latest_version)

        releaser = self.Releaser(configuration)
        manager = self.ResourceSignatureManager()
        api_name = configuration.api_name

        if self.should_create_resource_version(manager, api_name, current_version, latest_version):
            resource_version = self.create_resource_version(
                releaser=releaser,
                current_version=current_version,
                title=title or definition.get("title", ""),
                comment=comment or definition.get("comment", ""),
            )
            manager.reset_dirty(api_name)

            self.generate_sdks(
                releaser=releaser,
                resource_version=resource_version,
                *args,
                **kwargs,
            )
        else:
            print("resource_version already exists and is the latest, skip creating")

        result = releaser.release(
            version=resource_version.get("version", ""),
            resource_version_name=resource_version["name"],
            title=title or resource_version.get("title", ""),
            comment=comment or resource_version.get("comment", ""),
            stage_names=stage,
        )
        print(
            "API gateway released %s, title %s, stages %s"
            % (result.get("version"), result["resource_version_title"], result["stage_names"])
        )
