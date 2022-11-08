# -*- coding: utf-8 -*-
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
    return ServiceInstance.objects.create(service=service, plan=plan)


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
