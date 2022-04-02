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

from packaging.version import parse as parse_version

from apigw_manager.apigw.command import DefinitionCommand
from apigw_manager.apigw.helper import ResourceSignatureManager
from apigw_manager.core.fetch import Fetcher
from apigw_manager.core.release import Releaser


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

        parser.add_argument("-s", "--stage", default=[], nargs="+", help="release stages")

    def get_version_from_definition(self, definition):
        for k in ["version", "title"]:
            value = definition.get(k)
            if not value:
                continue

            return parse_version(value)

    def get_version_from_resource_version(self, resource_version):
        if not resource_version:
            return None

        for k in ["version", "title"]:
            value = resource_version.get(k)
            if not value:
                continue

            return parse_version(value)

    def fix_version(self, current_version, latest_version):
        # 没有发布记录且没配置版本
        if current_version is None and latest_version is None:
            return parse_version("0.0.1"), parse_version("?")

        # 没有发布过
        if latest_version is None:
            return current_version, parse_version("?")

        # 没有配置版本
        if current_version is None:
            # 加上当前时间作为元数据，但不改变版本优先级
            now = self.now_func()
            current_version = parse_version("%s+%s" % (latest_version.public, now.strftime("%Y%m%d%H%M%S")))

        return current_version, latest_version

    def create_resource_version(self, releaser, api_name, current_version, latest_version):
        manager = self.ResourceSignatureManager()

        # 版本一致，且没有变更
        if current_version.public == latest_version.public and not manager.is_dirty(api_name):
            return None

        version = str(current_version)
        resource_version = releaser.create_resource_version(version=version)
        manager.reset_dirty(api_name)

        return resource_version

    def handle(self, stage, *args, **kwargs):
        configuration = self.get_configuration(**kwargs)
        fetcher = self.Fetcher(configuration)
        resource_version = fetcher.latest_resource_version()
        latest_version = self.get_version_from_resource_version(resource_version)

        definition = self.get_definition(**kwargs)
        current_version = self.get_version_from_definition(definition)

        current_version, latest_version = self.fix_version(current_version, latest_version)

        releaser = self.Releaser(configuration)

        created_resource_version = self.create_resource_version(
            releaser,
            configuration.api_name,
            current_version,
            latest_version,
        )
        if created_resource_version:
            resource_version = created_resource_version
        else:
            print("resource_version already exists and is the latest, skip creating")

        result = releaser.release(
            resource_version_name=resource_version["name"],
            stage_names=stage,
        )
        print(
            "API gateway released %s, title %s, stages %s"
            % (result["resource_version_name"], result["resource_version_title"], result["stage_names"])
        )
