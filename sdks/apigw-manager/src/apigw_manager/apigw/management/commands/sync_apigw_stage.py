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

from apigw_manager.apigw.command import SyncCommand


class Command(SyncCommand):
    """Synchronous API gateway stage configuration"""

    default_namespace = "stage"

    def get_definition(self, define, file, namespace, **kwargs):
        definition = self.load_definition(define, file, **kwargs)
        if definition is None:
            return {}
        if definition.spec_version == 2:
            namespace = "stages"
            self.default_namespace = "stages"
        return super().get_definition(define, file, namespace, **kwargs)

    def do(self, manager, definition, *args, **kwargs):
        if self.default_namespace == "stages":
            for stage_definition in definition:
                result = manager.sync_stage_config(**stage_definition)
                print("API gateway stage synchronization completed, id %s, name %s" % (result["id"], result["name"]))
        else:
            result = manager.sync_stage_config(**definition)
            print("API gateway stage synchronization completed, id %s, name %s" % (result["id"], result["name"]))
