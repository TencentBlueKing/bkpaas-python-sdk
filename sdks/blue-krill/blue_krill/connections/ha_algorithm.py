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
import operator
import random
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .ha_endpoint_pool import Endpoint


class BasicHAAlgorithm:
    # 3 times lead to isolate
    failure_threshold: int = 3
    # 20s auto recover isolated endpoint
    default_isolated_duration: datetime.timedelta = datetime.timedelta(seconds=20)

    @staticmethod
    def _find_tops(endpoints: List['Endpoint']) -> List['Endpoint']:
        """
        find endpoints whose own biggest score

        example:

            input: [20, 50, 50, 100, 30, 100, 100]
            output: [100, 100, 100]
        """
        if not endpoints:
            raise ValueError("endpoints should not be empty during finding tops")

        sorted_endpoints = sorted(endpoints, key=operator.attrgetter('score'), reverse=True)
        return [x for x in sorted_endpoints if x.score == sorted_endpoints[0].score]

    def find_best_endpoint(self, endpoints: List['Endpoint']) -> 'Endpoint':
        """elect by score + random choice"""
        return random.choice(self._find_tops(endpoints))

    def should_be_isolated(self, endpoint: 'Endpoint') -> bool:
        """simple isolate method"""
        return endpoint.failure_count >= self.failure_threshold

    def should_be_recovered(self, endpoint: 'Endpoint') -> bool:
        """simple recover method"""
        if not endpoint.last_failure_time:
            return True
        return datetime.datetime.now() - endpoint.last_failure_time >= self.default_isolated_duration
