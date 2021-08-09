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
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def setting(name, default=None, strict=False):
    """
    Helper function to get a Django setting by name. If setting doesn't exists
    it can return a default or raise an error if in strict mode.

    :param name: Name of setting
    :type name: str
    :param default: Value if setting is unfound
    :param strict: Define if return default value or raise an error
    :type strict: bool
    :returns: Setting's value
    :raises: django.core.exceptions.ImproperlyConfigured if setting is unfound
             and strict mode
    """
    if strict and not hasattr(settings, name):
        msg = "You must provide settings.%s" % name
        raise ImproperlyConfigured(msg)
    return getattr(settings, name, default)


def get_setting(names, allow_env=True):
    """Get settings from settings first, then find in env vars

    :param list names: possible variable names
    :param bool allow_env: search variable in system env vars or not, default to True
    """
    names = [names] if not isinstance(names, (list, tuple)) else names
    for name in names:
        value = setting(name)
        if value is not None:
            break

    if value is None and allow_env:
        for name in names:
            value = os.environ.get(name)
            if value is not None:
                break
    return value
