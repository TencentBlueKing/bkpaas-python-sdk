# -*- coding: utf-8 -*-
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
