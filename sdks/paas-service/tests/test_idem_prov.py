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
import pytest

from paas_service.idem_prov import idempotent_provision_instance, mark_record_success
from paas_service.constants import ProvisionRecordStatus
from paas_service.models import ProvisionRecord
from paas_service.base_vendor import InstanceData

pytestmark = pytest.mark.django_db

class DummyProvider:
    def __init__(self, **kwargs):
        pass

    def create(self, params):
        return InstanceData(
            credentials={"host": "1.2.3.4", "password": "pass"},
            config={"endpoint": "http://example.com"},
        )

class FailingProvider:
    def __init__(self, **kwargs):
        pass

    def create(self, params):
        raise Exception("Provisioning failed")

class TestIdempotentProvision:
    def test_idempotent_provision_instance(self, service, plan):
        # 模拟 provider 创建实例成功
        # 第一次调用，应该创建实例
        instance1, created1 = idempotent_provision_instance(
            provision_key='key1',
            service=service,
            plan=plan,
            params={},
            provider_cls_getter=lambda: DummyProvider,
        )
        assert created1 is True
        assert instance1 is not None
        assert ProvisionRecord.objects.filter(provision_key='key1', status=ProvisionRecordStatus.SUCCESS).exists()

        # 第二次调用，应该复用实例
        instance2, created2 = idempotent_provision_instance(
            provision_key='key1',
            service=service,
            plan=plan,
            params={},
            provider_cls_getter=lambda: DummyProvider
        )
        assert created2 is False
        assert instance2 == instance1
    
    def test_idem_prov_failure(self, service, plan):
        with pytest.raises(Exception, match="Provisioning failed"):
            idempotent_provision_instance(
                provision_key='key2',
                service=service,
                plan=plan,
                params={},
                provider_cls_getter=lambda: FailingProvider,
            )

        assert not ProvisionRecord.objects.filter(provision_key='key2').exists()
    
    def test_mark_record_success(self, instance, provisioning_record):
        assert provisioning_record.status == ProvisionRecordStatus.PROVISIONING
        mark_record_success(provisioning_record, instance)

        provisioning_record.refresh_from_db()
        assert provisioning_record.status == ProvisionRecordStatus.SUCCESS
        assert provisioning_record.service_instance == instance
