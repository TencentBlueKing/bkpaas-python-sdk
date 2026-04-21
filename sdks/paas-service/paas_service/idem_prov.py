from datetime import timedelta
import json
from typing import Callable

from django.db import IntegrityError, transaction
from django.utils import timezone

from paas_service.base_vendor import BaseProvider, get_provider_cls
from paas_service.models import Plan, Service

from .constants import ProvisionRecordStatus, MAX_PROVISION_TIMEOUT_SECONDS
from .models import ProvisionRecord, ServiceInstance


def idempotent_provision_instance(
    provision_key: str,
    service: Service,
    plan: Plan,
    params: dict,
    provider_cls_getter: Callable[[], type[BaseProvider]] = get_provider_cls,
) -> tuple[ServiceInstance | None, bool]:
    """Create or reuse instance by provision key

    Returns:
        (service_instance, created)
        `service_instance=None` when provisioning
    """
    
    try:
        with transaction.atomic():
            record = ProvisionRecord.objects.create(
                provision_key=provision_key,
                plan_id=plan.uuid,
                status=ProvisionRecordStatus.PROVISIONING,
            )
            acquired = True
    except IntegrityError:
        acquired = False
    
    if not acquired:
        record = ProvisionRecord.objects.select_related('service_instance').get(
            provision_key=provision_key,
        )
        if record.status == ProvisionRecordStatus.SUCCESS:
            return record.service_instance, False
        if record.status == ProvisionRecordStatus.PROVISIONING:
            return None, False
        raise Exception(f"Provision record with key {provision_key} is in unexpected status {record.status}")

    provider_cls = provider_cls_getter()
    plan_config = json.loads(plan.config)
    try:
        instance_data = provider_cls(**plan_config).create(params=params)
    except Exception:
        record.delete()
        raise

    service_instance = ServiceInstance.objects.create(
        service=service,
        plan=plan,
        config=instance_data.config,
        credentials=json.dumps(instance_data.credentials),
        tenant_id=plan.tenant_id,
    )
    mark_record_success(record, service_instance)
    return service_instance, True


def mark_record_success(record: ProvisionRecord, service_instance: ServiceInstance):
    record.service_instance = service_instance
    record.status = ProvisionRecordStatus.SUCCESS
    record.save(update_fields=["service_instance", "status"])
