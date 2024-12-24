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
from typing import Optional

from paas_service.models import Plan, Service, ServiceInstance, SpecDefinition, Specification
from rest_framework import serializers


class SpecDefinitionSLZ(serializers.ModelSerializer):
    class Meta(object):
        model = SpecDefinition
        exclude = ['index', 'uuid', 'created', 'updated']


class ServiceSLZ(serializers.ModelSerializer):
    specifications = serializers.ListField(child=SpecDefinitionSLZ(), source='specifications.all')
    logo = serializers.SerializerMethodField()
    config = serializers.JSONField()

    def get_logo(self, obj):
        # type: (Service) -> Optional[str]
        if obj.logo:
            return obj.logo
        elif obj.logo_url:
            return obj.logo_url
        else:
            return None

    class Meta(object):
        model = Service
        exclude = ['created', 'updated']


class PlanSLZ(serializers.ModelSerializer):
    properties = serializers.JSONField()
    config = serializers.JSONField(source="get_config")
    specifications = serializers.DictField(source='full_specifications')

    class Meta(object):
        model = Plan
        exclude = ['created', 'updated']


class ServiceListSLZ(ServiceSLZ):
    plans = serializers.ListField(child=PlanSLZ(), source='plans.all')


class ServiceInstanceSLZ(serializers.ModelSerializer):
    def to_representation(self, instance: ServiceInstance):
        instance_info = super(ServiceInstanceSLZ, self).to_representation(instance)
        instance_info.update(instance.render())
        return instance_info

    class Meta(object):
        model = ServiceInstance
        exclude = ['config', 'credentials']


class ServiceInstanceQuerySLZ(serializers.Serializer):
    to_be_deleted = serializers.BooleanField(required=False, default=False)


class ServiceInstanceBinderSLZ(serializers.Serializer):
    config = serializers.DictField(required=False, default=dict)
    credentials = serializers.DictField(required=True)


class PaaSAppInfoSLZ(serializers.Serializer):
    """Serializer for Application Info from Blueking PaaS.

    Only `app_id` was required.
    """

    app_id = serializers.CharField(max_length=64)
    app_code = serializers.CharField(max_length=64, default='')
    app_name = serializers.CharField(max_length=64, default='')
    module = serializers.CharField(max_length=64, default='')
    environment = serializers.CharField(max_length=32, default='unknown')


class InstanceConfigSLZ(serializers.Serializer):
    paas_app_info = PaaSAppInfoSLZ(required=True)


############################
# Serializer for admin api #
############################
class _SpecDefinitionUpsertSLZ(serializers.ModelSerializer):
    name = serializers.CharField(help_text='名称', max_length=64)

    def to_internal_value(self, data):
        try:
            instance = SpecDefinition.objects.get(name=data["name"])
            for k, v in data.items():
                setattr(instance, k, v)
        except SpecDefinition.DoesNotExist:
            instance = SpecDefinition(**data)
        return instance

    class Meta(object):
        model = SpecDefinition
        exclude = ['index', 'uuid', 'created', 'updated']


class ServiceUpsertSLZ(serializers.ModelSerializer):
    """Usage
    # For Update
    >>> slz = ServiceUpsertSLZ(data={}, instance=service)
    >>> slz.is_valid(True)
    >>> slz.save()

    # For Create
    >>> slz = ServiceUpsertSLZ(data={})
    >>> slz.is_valid(True)
    >>> slz.save()
    """

    specifications = serializers.ManyRelatedField(child_relation=_SpecDefinitionUpsertSLZ())
    config = serializers.JSONField()

    def update(self, instance, validated_data):
        for spec_def in validated_data["specifications"]:
            spec_def.save()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        for spec_def in validated_data["specifications"]:
            spec_def.save()
        return super().create(validated_data)

    class Meta(object):
        model = Service
        fields = "__all__"


class _SpecificationUpsertSLZ(serializers.JSONField):
    def to_internal_value(self, data):
        specifications = []
        for key, value in data.items():
            definition = SpecDefinition.objects.get(name=key)
            try:
                specifications.append(Specification.objects.get(definition=definition, value=value))
            except Specification.DoesNotExist:
                specifications.append(Specification.objects.create(definition=definition, value=value))
        return specifications


class PlanUpsertSLZ(serializers.ModelSerializer):
    """Usage
    # For Update
    >>> slz = PlanUpsertSLZ(data={}, instance=plan)
    >>> slz.is_valid(True)
    >>> slz.save()

    # For Create
    >>> slz = PlanUpsertSLZ(data={})
    >>> slz.is_valid(True)
    >>> slz.save()
    """

    def save(self, **kwargs):
        # 剔除 region 字段, 避免 create 出错
        region = self.validated_data.pop("region", None)
        instance = super().save(**kwargs)
        # 更新 region 字段.
        if region:
            instance.properties["region"] = region
            instance.save()
        return instance

    region = serializers.CharField()

    properties = serializers.JSONField()
    specifications = _SpecificationUpsertSLZ()

    class Meta(object):
        model = Plan
        exclude = ['created', 'updated']
