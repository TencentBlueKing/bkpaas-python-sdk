# -*- coding: utf-8 -*-
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
