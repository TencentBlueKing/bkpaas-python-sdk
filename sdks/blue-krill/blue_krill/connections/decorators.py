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
import functools

from .exceptions import NoEndpointAvailable


def use_algo_as_default(method_name):
    """use algorithm's method if no custom method pass in
    :param method_name: method name in algorithm class
    :return:
    """

    def _wrapper(func):
        @functools.wraps(func)
        def _wrapped(self, method=None, *args, **kwargs):
            if not method:
                # NOTE: the method param name is fixed(`method`)
                method = getattr(self.algorithm, method_name)
            return func(self, method, *args, **kwargs)

        return _wrapped

    return _wrapper


def elect_if_no_active_ep(func):
    """if there is no active endpoint, we will elect one before function"""

    @functools.wraps(func)
    def _wrapped(self, *args, **kwargs):
        if not self.active:
            self.elect()
        return func(self, *args, **kwargs)

    return _wrapped


def raise_if_no_data(func):
    """raise NoEndpointAvailable if there is no data in pool"""

    @functools.wraps(func)
    def _wrapped(self, *args, **kwargs):
        if not self.data:
            raise NoEndpointAvailable("no Endpoint available in pool")
        return func(self, *args, **kwargs)

    return _wrapped
