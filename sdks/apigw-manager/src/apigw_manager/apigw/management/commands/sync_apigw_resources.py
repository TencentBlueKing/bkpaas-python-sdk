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
from apigw_manager.apigw.command import SyncCommand


class Command(SyncCommand):
    """Synchronous API Gateway resources"""

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument(
            "--delete",
            default=False,
            action="store_true",
            help="delete extraneous resources from existing resources",
        )

    def do(self, manager, definition, *args, **kwargs):
        result = manager.sync_resources_config(content=definition, delete=kwargs["delete"])

        added = result["added"]
        deleted = result["deleted"]
        updated = result["updated"]

        print(
            "API gateway resources synchronization completed, added %s, updated %s, deleted %s"
            % (len(added), len(updated), len(deleted))
        )
