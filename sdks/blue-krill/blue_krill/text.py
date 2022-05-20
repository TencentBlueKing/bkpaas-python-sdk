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
import sys

from blue_krill.data_types.url import MutableURL


def remove_suffix(s: str, suffix: str) -> str:
    """If given string endswith `suffix`, remove the suffix and return the new string"""
    if sys.version_info >= (3, 9):
        return s.removesuffix(suffix)
    if s.endswith(suffix):
        return s[: -len(suffix)]
    return s


def remove_prefix(s: str, prefix: str) -> str:
    """If given string startswith `prefix`, remove the prefix and return the new string"""
    if sys.version_info >= (3, 9):
        return s.removeprefix(prefix)
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


def desensitize_url(url: str) -> str:
    """Obscure the password field in the url

    >>> desensitize_url("scheme://username:password@hostname:6666/path/?foo=bar")
    "scheme://username:********@hostname:6666/path/?foo=bar"
    """
    return MutableURL(url).obscure()
