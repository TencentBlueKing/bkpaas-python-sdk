# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from blue_krill.data_types.url import MutableURL


def remove_suffix(s: str, suffix: str) -> str:
    """If given string endswith `suffix`, remove the suffix and return the new string"""
    return s.removesuffix(suffix)


def remove_prefix(s: str, prefix: str) -> str:
    """If given string startswith `prefix`, remove the prefix and return the new string"""
    return s.removeprefix(prefix)


def desensitize_url(url: str) -> str:
    """Obscure the password field in the url

    >>> desensitize_url("scheme://username:password@hostname:6666/path/?foo=bar")
    "scheme://username:********@hostname:6666/path/?foo=bar"
    """
    return MutableURL(url).obscure()


def mask_secret(value: str, keep_tail: int = 6, min_length: int = 20) -> str:
    """Mask a secret value so that it can be logged. Only the last `keep_tail` characters are kept, the
    rest is replaced by a fixed length mask so that the length of the value is not exposed. The value is
    masked completely when it's too short, so that no more than 1/4 of the characters are exposed.

    NOTE: Only use it on long random values such as API tokens or JWT signatures, never on passwords or
    the value of Basic auth, the tail of which is exactly the tail of the password.

    >>> mask_secret("SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    "***Qssw5c"
    """
    if keep_tail <= 0 or len(value) < max(min_length, keep_tail * 4):
        return "******"
    return "***" + value[-keep_tail:]
