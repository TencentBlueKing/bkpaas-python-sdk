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
import uuid
from typing import Any, Dict, List

from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField
from translated_fields import TranslatedField

from blue_krill.models.fields import EncryptField

# Base Models start


class AuditedModel(models.Model):
    """Audited model with 'created' and 'updated' fields."""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class UuidAuditedModel(AuditedModel):
    """Add a UUID primary key to an :class:`AuditedModel`."""

    uuid = models.UUIDField(
        'UUID', default=uuid.uuid4, primary_key=True, editable=False, auto_created=True, unique=True
    )

    class Meta(object):
        abstract = True


# Base Models end


class SpecDefinition(UuidAuditedModel):
    """Specification definition"""

    index = models.IntegerField(verbose_name=_('顺序'), default=0)
    name = models.CharField(verbose_name=_('名称'), unique=True, max_length=64, null=True)
    display_name = TranslatedField(models.CharField(verbose_name=_('展示名称'), max_length=128, blank=True))
    description = models.TextField(verbose_name=_('描述'), blank=True)
    recommended_value = models.CharField(verbose_name=_('推荐值'), max_length=64, blank=True, null=True)

    class Meta:
        verbose_name_plural = verbose_name = _('规格定义')
        ordering = ['index', 'name']

    def __str__(self):
        return f"{self.display_name}"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.name
        super().save(*args, **kwargs)


class Specification(UuidAuditedModel):
    """Specification value"""

    definition = models.ForeignKey(SpecDefinition, verbose_name=_('定义'), on_delete=models.CASCADE)
    value = models.CharField(verbose_name=_('值'), max_length=64)
    display_name = TranslatedField(models.CharField(verbose_name=_('展示名称'), max_length=64, blank=True))

    class Meta:
        verbose_name_plural = verbose_name = _('规格')
        unique_together = ['definition', 'value']

    def __str__(self):
        return f"{self.definition}:{self.display_name}"

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.value
        super().save(*args, **kwargs)


class Service(UuidAuditedModel):
    """Service model for PaaS"""

    name = models.CharField(verbose_name='服务名称', unique=True, max_length=64)
    category = models.IntegerField(verbose_name='服务分类')
    display_name = TranslatedField(models.CharField(verbose_name=_('服务全称'), max_length=128))
    logo_url = models.URLField(verbose_name='服务 logo 地址', null=True, blank=True)
    logo = models.TextField(verbose_name='服务 logo base64', null=True, blank=True)

    description = TranslatedField(models.CharField(verbose_name=_('简介'), max_length=1024, blank=True))
    long_description = TranslatedField(models.TextField(verbose_name=_('详细介绍'), blank=True))
    instance_tutorial = TranslatedField(models.TextField(verbose_name=_('实例内页介绍'), blank=True))

    available_languages = models.CharField(verbose_name=_('支持编程语言'), max_length=1024, null=True, blank=True)
    config = JSONField(default=dict, blank=True)
    is_active = models.BooleanField(verbose_name='是否可用', default=True)
    is_visible = models.BooleanField(verbose_name="是否可见", default=True)

    specifications = models.ManyToManyField(SpecDefinition, verbose_name='规格定义', blank=True)

    class Meta:
        verbose_name_plural = verbose_name = '服务'

    def __str__(self):
        return f"{self.name}"


class ServiceInstance(UuidAuditedModel):
    """specific info of service"""

    _prepared_fields_data = None

    service = models.ForeignKey('Service', verbose_name='服务', null=True, on_delete=models.SET_NULL)
    plan = models.ForeignKey(
        'Plan', verbose_name='方案', null=True, help_text="当前仅当迁移的增强服务实例, 会没有 plan", on_delete=models.SET_NULL
    )
    config = JSONField(default=dict, blank=True)
    credentials = EncryptField(default="")
    to_be_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = verbose_name = '服务实例'

    def __str__(self):
        return f"{self.service}-{self.plan}-{self.uuid}"

    def get_credentials(self):
        return json.loads(self.credentials)

    @property
    def from_client_side(self):
        """描述该实例是否由 'client-side' 创建, 远程增强服务中负责存储实例的 credentials, config 信息"""
        return self.plan is None

    def prerender(self, request: HttpRequest):
        """Prepare for rendering data to client"""
        # Allow other services to override default render logic
        func = import_string(
            getattr(settings, 'PAAS_SERVICE_SVC_INSTANCE_RENDER_FUNC', 'paas_service.models.render_instance_data')
        )
        data = func(request, self)
        self._prepared_fields_data = data

    def render(self):
        if not self._prepared_fields_data:
            raise ValueError('no prerendered data found, please call prerender method first')
        return self._prepared_fields_data


class ServiceInstanceConfig(UuidAuditedModel):
    """Extra config for instance"""

    instance = models.OneToOneField(ServiceInstance, verbose_name='服务实例', on_delete=models.CASCADE)
    paas_app_info = JSONField(default=dict, blank=True, verbose_name='平台应用信息')

    def was_initialized(self) -> bool:
        """Return if current config object was initialized"""
        return bool(self.paas_app_info)


class InstanceDataRepresenter:
    """represents service instance"""

    def __init__(self, request: HttpRequest, instance: ServiceInstance):
        self.request = request
        self.instance = instance

        # Set initial values for config/credentials
        self._config = self.instance.config
        self._credentials = json.loads(self.instance.credentials)
        # Meta config is a field which store meta options
        self.meta_config: Dict[str, Any] = {}

    def set_hidden_fields(self, hidden_fields: List):
        """Set fields as hidden"""
        self.meta_config['should_hidden_fields'] = hidden_fields

    def set_removed_fields(self, fields: List):
        self.meta_config['should_remove_fields'] = fields

    def represent(self) -> Dict:
        return {
            'config': {'__meta__': self.meta_config, **self._config},
            'credentials': self._credentials,
        }


def render_instance_data(request: HttpRequest, instance: ServiceInstance) -> Dict:
    """Default render function for rendering service instance data"""
    return InstanceDataRepresenter(request, instance).represent()


class Plan(UuidAuditedModel):
    name = models.CharField(verbose_name='方案名称', max_length=64)

    # the "properties" field stores custom properties of a plan object. the property itself is
    # nothing more than a simple annotation. But the service hub which it was registed to may
    # take special actions according to these annotations.
    #
    # Some example properties: {"region": "r1", "as_env_default": "prod" ... ...}
    properties = JSONField(default=dict, blank=True)

    description = models.CharField(verbose_name='方案简介', max_length=1024, blank=True)
    config = EncryptField(verbose_name='方案配置', default="", blank=True)
    is_active = models.BooleanField(verbose_name='是否可用', default=True)
    service = models.ForeignKey('Service', related_name='plans', verbose_name='服务', on_delete=models.CASCADE)

    specifications = models.ManyToManyField(Specification, verbose_name='规格', blank=True)

    class Meta:
        verbose_name_plural = verbose_name = '方案'
        unique_together = ("service", "name")

    def __str__(self):
        return f"{self.name}-{self.service.name}"

    def get_config(self):
        return json.loads(self.config)

    @cached_property
    def full_specifications(self) -> Dict[str, Any]:
        # 已定义的全量规格,默认为 None
        specifications = dict.fromkeys(d.name for d in self.service.specifications.all())

        # 填充真实值
        for spec in self.specifications.filter(definition__name__in=specifications.keys(),).prefetch_related(
            "definition"
        ):  # type: Specification
            specifications[spec.definition.name] = spec.value

        return specifications


class ResourceId(models.Model):
    """utility model for avoiding name conflict"""

    namespace = models.CharField(max_length=32)
    uid = models.CharField(max_length=64, null=False, unique=True, db_index=True)

    class Meta(object):
        unique_together = ('namespace', 'uid')

    def __str__(self):
        return f"{self.namespace}-{self.uid}"
