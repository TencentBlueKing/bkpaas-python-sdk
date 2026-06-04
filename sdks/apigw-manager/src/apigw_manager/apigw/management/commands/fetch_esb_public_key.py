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

import copy

from apigw_manager.apigw.management.commands.fetch_apigw_public_key import Command as BaseCommand


class Command(BaseCommand):
    """Get the esb public key and store it into the database"""

    def handle(self, gateway_name, *args, **kwargs):
        copied_kwargs = copy.deepcopy(kwargs)

        for _gateway_name in ["bk-esb", "apigw"]:
            copied_kwargs["gateway_name"] = _gateway_name
            super(Command, self).handle(*args, **copied_kwargs)
