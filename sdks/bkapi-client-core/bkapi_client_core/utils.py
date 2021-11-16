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
import copy
from functools import wraps
from typing import Callable, Optional, Type, TypeVar

import curlify
import requests


def urljoin(base_url, path):
    # type: (str, str) -> str
    if not base_url:
        return path

    if not path:
        return base_url

    return "%s/%s" % (base_url.rstrip("/"), path.lstrip("/"))


def to_curl(request):
    # type: (Optional[requests.PreparedRequest]) -> str
    if request is None:
        return ""

    try:
        # if request.body contains binary content, it may not be decoded
        return curlify.to_curl(request)
    except UnicodeDecodeError:
        copied_request = copy.deepcopy(request)
        copied_request.body = ""
        return curlify.to_curl(copied_request)


T = TypeVar("T")


def generic_type_partial(cls, fn):
    # type: (Type[T], Callable) -> Callable[..., T]
    """A tool for wraps function with generic type"""

    @wraps(fn)
    def f(*args, **kwargs):
        return fn(cls, *args, **kwargs)

    return f
