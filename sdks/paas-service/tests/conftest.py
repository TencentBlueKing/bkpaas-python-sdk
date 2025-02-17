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
from paas_service.auth.backends import Client
from paas_service.models import Plan, Service, ServiceInstance, SpecDefinition


@pytest.fixture
def service():
    return Service.objects.create(
        name='s1',
        category=1,
        display_name_zh_cn='我的增强服务',
        display_name_en='service NO.1',
    )


@pytest.fixture
def plan(service):
    return Plan.objects.create(name="plan-default", properties={}, service=service, config='{}')


@pytest.fixture
def instance(service, plan):
    return ServiceInstance.objects.create(service=service, plan=plan,tenant_id=plan.tenant_id)


@pytest.fixture
def instance_with_credentials(service, plan):
    credentials = """
    {"host": "host.test", "port": "0000", "name": "bkapp-test", "user": "bkapp-test", "password": "password"}
    """
    return ServiceInstance.objects.create(service=service, plan=plan,credentials=credentials,tenant_id=plan.tenant_id)


@pytest.fixture
def spec_def(service):
    spec_def = SpecDefinition.objects.create(
        **{
            "name": "foo",
            "display_name_zh_cn": "简介",
            "display_name_en": "FOO",
            "description": "this is foo.",
            "recommended_value": "Foo",
        }
    )
    service.specifications.set([spec_def])
    return spec_def


@pytest.fixture
def platform_client():
    """An authenticated client object"""
    return Client('test_client', role='internal_platform')
