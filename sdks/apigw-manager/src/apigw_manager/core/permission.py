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

from apigw_manager.core.handler import Handler


class Manager(Handler):
    """Manage API Gateway Permissions"""

    def apply_permission(self, *args, **kwargs):
        """Apply for API Gateway Permissions"""
        result = self._call_v2(self.client.api.v2_open_apply_gateway_permission, *args, **kwargs)
        return self._parse_v2_result(result)

    def grant_permission(self, *args, **kwargs):
        """Grant API gateway permissions for applications"""
        result = self._call_v2(self.client.api.v2_sync_grant_permission, *args, **kwargs)
        return self._parse_v2_result(result)
