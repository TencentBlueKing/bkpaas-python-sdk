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
from apigw_manager.core.exceptions import ApiResponseError


class Command(SyncCommand):
    """Add related apps for gateway"""

    default_namespace = "related_apps"

    def do(self, manager, definition, *args, **kwargs):
        if not definition:
            print("no related apps found, skip")
            return

        try:
            manager.add_related_apps(target_app_codes=definition)
        except ApiResponseError as err:
            print("warning!! Add related apps error, %s" % str(err))
            return

        print("Add related apps for gateway %s: %s" % (manager.config.gateway_name, ", ".join(definition)))
