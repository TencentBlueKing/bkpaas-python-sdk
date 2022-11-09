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
import logging
from collections.abc import Mapping
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


def instance_authorized_require(func):
    """Decorator for view methods which use an "instance_id" as first argument,
    will check session to see if instance_id requested has been authorized via
    backends.
    """

    @wraps(func)
    def wrapper(request, instance_id, *args, **kwargs):
        authorized_instances = request.session.get('authorized_instances', {})
        if not isinstance(authorized_instances, Mapping):
            logger.error('authorized_instances type error')
            return HttpResponseServerError('internal server error, please try again')

        # Check if instance has been authorized
        if instance_id not in authorized_instances:
            raise PermissionDenied()

        return func(request, instance_id, *args, **kwargs)

    return wrapper


def verified_client_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        client = getattr(request, 'client', None)
        if client and client.is_verified():
            return func(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    return wrapper


def verified_client_role_require(role_name):
    """check if role exist with covering features of the above decorator"""

    @method_decorator
    def _wrapper(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            client = getattr(request, 'client', None)
            if client and client.is_verified() and role_name == client.role:
                return func(request, *args, **kwargs)
            else:
                raise PermissionDenied()

        return _wrapped

    return _wrapper
