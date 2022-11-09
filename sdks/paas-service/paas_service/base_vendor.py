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
from abc import ABCMeta, abstractmethod
from typing import ClassVar, Dict, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


def get_provider_cls():
    try:
        SVC_PROVIDER_CLS = settings.PAAS_SERVICE_PROVIDER_CLS
    except AttributeError:
        raise ImproperlyConfigured("PAAS_SERVICE_PROVIDER_CLS is not configured")

    return import_string(SVC_PROVIDER_CLS)


class BaseVendorException(Exception):
    """Base class for vendor exception"""


class ArgumentInvalidError(BaseVendorException):
    """raised when given argument is invalid"""


class OperationFailed(BaseVendorException):
    """raised when operation fails"""


class InstanceData:
    __slots__ = ['credentials', 'config']

    def __init__(self, credentials, config=None):
        self.credentials = credentials
        self.config = config


class BaseProvider(metaclass=ABCMeta):
    SERVICE_NAME: ClassVar[Optional[str]] = None

    @abstractmethod
    def create(self, params: Dict) -> InstanceData:
        raise NotImplementedError

    @abstractmethod
    def delete(self, instanceData: InstanceData):
        raise NotImplementedError

    @abstractmethod
    def patch(self, instanceData: InstanceData, params: Dict) -> InstanceData:
        raise NotImplementedError


class DummyProvider(BaseProvider):
    SERVICE_NAME = 'dummy_svc'

    def create(self, params: Dict) -> InstanceData:
        return InstanceData(credentials={'foo': 'bar'}, config={'foo_config': 'bar_value'})

    def delete(self, instanceData: InstanceData):
        return

    def patch(self, instanceData: InstanceData, params: Dict) -> InstanceData:
        raise NotImplementedError
