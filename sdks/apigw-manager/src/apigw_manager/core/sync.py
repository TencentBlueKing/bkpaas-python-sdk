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

import yaml

from apigw_manager.core.handler import Handler


class Synchronizer(Handler):
    """Synchronous API gateway configuration"""

    def sync_basic_config(self, *args, **kwargs):
        result = self._call_v2(self.client.api.v2_sync_gateway, *args, **kwargs)
        return self._parse_v2_result(result)

    def sync_stage_config(self, *args, **kwargs):
        result = self._call_v2(self.client.api.v2_sync_stages, *args, **kwargs)
        return self._parse_v2_result(result)

    def sync_stage_mcp_servers(self, *args, **kwargs):
        result = self._call_v2(self.client.api.v2_sync_stage_mcp_servers, *args, **kwargs)
        return self._parse_v2_result(result)

    def sync_resources_config(self, content, *args, **kwargs):
        kwargs["content"] = yaml.dump(dict(content))

        result = self._call_v2(self.client.api.v2_sync_resources, *args, **kwargs)
        return self._parse_v2_result(result)

    def sync_resource_docs_by_archive(self, *args, **kwargs):
        result = self._call_v2(self.client.api.v2_sync_resource_doc, *args, **kwargs)
        return self._parse_v2_result(result)

    def add_related_apps(self, *args, **kwargs):
        kwargs["related_app_codes"] = kwargs.pop("related_apps")

        result = self._call_v2(self.client.api.v2_sync_add_related_apps, *args, **kwargs)
        return self._parse_v2_result(result)
