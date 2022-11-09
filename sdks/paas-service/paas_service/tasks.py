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
import json
import logging

from paas_service.base_vendor import InstanceData, get_provider_cls
from paas_service.models import ServiceInstance

logger = logging.getLogger(__name__)


def clean_instances():
    # why not values_list? Because we will use deleting_instance lately
    deleting_instances = ServiceInstance.objects.filter(to_be_deleted=True)

    if not deleting_instances:
        logging.info("nothing need to clean.")
        return

    for instance in deleting_instances:
        provider_cls = get_provider_cls()
        instance_data = InstanceData(
            credentials=json.loads(instance.credentials),
            config=instance.config,
        )
        plan_config = json.loads(instance.plan.config)
        try:
            provider_cls(**plan_config).delete(instance_data)
        except Exception as e:
            # remain deleting status if provider delete failed
            logger.exception(f"delete service instance<{instance.uuid}> failed: {e}")
            continue
        else:
            logger.info(f"instance<{instance.uuid}> will be cleaned. ")
            instance.delete()
