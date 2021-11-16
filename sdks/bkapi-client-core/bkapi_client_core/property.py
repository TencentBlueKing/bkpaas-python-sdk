# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
from typing import Any, Type, TypeVar

from typing_extensions import Protocol


class BindableProtocol(Protocol):
    """BindableProtocol is a protocol for lazy initialization and binding to a manager"""

    def bind(
        self,
        name,  # type: str
        manager,  # type: Any
    ):
        """Bind to manager with the specified name"""
        raise NotImplementedError


class BindProperty(object):
    """
    BindProperty is a API declaration specification of lazy initialization of Property.
    To help the IDE improve the intelligent completion experience,
    use the bind_property function instead of the class.
    """

    def __init__(
        self,
        cls,  # type: Type[BindableProtocol]
        *args,  # type: Any
        **kwargs  # type: Any
    ):
        self._name = ""
        self._property_id = "_bind_property_id_%s" % id(self)
        self._cls = cls
        self._args = args
        self._kwargs = kwargs

    def __set_name__(self, obj_type, name):
        self._name = name

    def __get__(self, obj, obj_type=None):
        if not obj:
            return self._cls

        # At least for Python 3.6 and higher
        # The __set_name__ method was included
        # which is automatically called when the class is being created
        # So in order to compatibility with low versions
        # we need to cache the property instance
        if hasattr(obj, self._property_id):
            return getattr(obj, self._property_id)

        value = self._cls(*self._args, **self._kwargs)  # type: ignore
        value.bind(self._name, obj)

        setattr(obj, self._name or self._property_id, value)

        return value


T = TypeVar("T", bound=BindableProtocol)


def bind_property(cls, *args, **kwargs):
    # type: (Type[T], *Any, **Any) -> T
    """The generic function wrapper for BindProperty"""

    return BindProperty(cls, *args, **kwargs)  # type: ignore
