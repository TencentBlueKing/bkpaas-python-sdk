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
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ha_endpoint_pool import Endpoint


class BasicHAAlgorithm:
    """Algorithm class which cooperates with `HAEndpointPool`, it decides how
    Endpoint recover or become unhealthy.
    """

    # Max attempts before consider endpoint as "unhealthy"
    unhealthy_max_failed: int = 3
    # Unhealthy Endpoint become healthy again after `unhealthy_period`
    unhealthy_period: datetime.timedelta = datetime.timedelta(seconds=20)

    def is_unhealthy(self, endpoint: 'Endpoint') -> bool:
        """Whether given endpoint is unhealthy"""
        return endpoint.failure_count >= self.unhealthy_max_failed

    def should_recover(self, endpoint: 'Endpoint') -> bool:
        """Whether an unhealthy endpoint should be recovered"""
        if not endpoint.unhealthy_at:
            return False
        return (datetime.datetime.now() - endpoint.unhealthy_at) >= self.unhealthy_period
