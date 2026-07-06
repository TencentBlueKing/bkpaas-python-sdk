# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from apigw_manager.apigw.command import PermissionCommand


class Command(PermissionCommand):
    """Apply for API Gateway Permissions"""

    default_namespace = "apply_permissions"

    def do(self, manager, definition, *args, **kwargs):
        if not definition:
            print("no permission apply definition found, skip")
            return

        for permission in definition:
            permission.setdefault("target_app_code", manager.config.bk_app_code)
            permission.setdefault("applicant", permission["target_app_code"])

            # v2 使用 gateway_name 替代 api_name
            if "api_name" in permission:
                permission["gateway_name"] = permission.pop("api_name")

            if permission.get("grant_dimension") is None:
                permission["grant_dimension"] = "gateway"

            result = manager.apply_permission(**permission)
            print(
                "Applied permissions for gateway %s, record %s, dimension %s"
                % (
                    permission.get("gateway_name", manager.config.gateway_name),
                    result["record_id"],
                    permission["grant_dimension"],
                )
            )
