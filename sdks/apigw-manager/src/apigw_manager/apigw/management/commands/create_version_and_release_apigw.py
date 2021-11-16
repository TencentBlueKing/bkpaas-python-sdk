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
from apigw_manager.apigw.command import DefinitionCommand
from apigw_manager.apigw.helper import ReleaseVersionManager
from apigw_manager.core.fetch import Fetcher
from apigw_manager.core.release import Releaser


class Command(DefinitionCommand):
    """API gateway release a version"""

    default_namespace = "release"
    Fetcher = Fetcher
    Releaser = Releaser

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument("-t", "--title", default=None, help="resource version title")
        parser.add_argument("-c", "--comment", default="", help="release comment")
        parser.add_argument("-s", "--stage", default=[], nargs="+", help="release stages")

    def _should_create_resource_version(self, resource_version, title):
        if not resource_version:
            return True

        return resource_version.get("title") != title

    def get_default_version_title(self, configuration):
        manager = ReleaseVersionManager()
        return manager.increase(configuration.api_name)

    def handle(self, title, comment, stage, *args, **kwargs):
        configuration = self.get_configuration(**kwargs)
        definition = self.get_definition(**kwargs)

        title = title or definition.get("title") or self.get_default_version_title(configuration=configuration)
        comment = comment or definition.get("comment", "")

        fetcher = self.Fetcher(configuration)
        releaser = self.Releaser(configuration)

        resource_version = fetcher.latest_resource_version()
        if self._should_create_resource_version(resource_version, title):
            resource_version = releaser.create_resource_version(title=title, comment=comment)
        else:
            print("resource_version already exists and is the latest, skip creating")

        result = releaser.release(
            resource_version_name=resource_version["name"],
            comment=comment,
            stage_names=stage,
        )
        print(
            "API gateway released %s, title %s, stages %s"
            % (result["resource_version_name"], result["resource_version_title"], result["stage_names"])
        )
