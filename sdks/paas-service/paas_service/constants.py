# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions and
limitations under the License.

We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""
from enum import Enum

from blue_krill.data_types.enum import StrStructuredEnum, EnumField


class Category(int, Enum):
    """Paas service categories"""

    DATA_STORAGE = 1
    MONITORING_HEALTHY = 2


class ProvisionRecordStatus(StrStructuredEnum):
    # 实例创建中
    PROVISIONING = EnumField("provisioning", label="分配资源中")
    # 成功：物理资源已创建
    SUCCESS = EnumField("success", label="分配成功")

    # 异步删除触发，或分配发生错误，都会直接删除 ProvisionRecord，所以无需对应的状态


# Login 服务的重定向链接字段名
REDIRECT_FIELD_NAME = "c_url"

# The default tenant id exists only if the project does not enable multi-tenant mode,
# it serves as a reserved value. When multi-tenant mode is enabled, no tenant id can
# be "default".
DEFAULT_TENANT_ID = "default"
