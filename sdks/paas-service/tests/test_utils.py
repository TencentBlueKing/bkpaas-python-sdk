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

import pytest
from paas_service.utils import Base36Handler, parse_redirect_params


@pytest.mark.parametrize(
    ("redirect_url", "kwargs", "expected"),
    [
        ("foo.bar.baz?a=1", {}, ("foo.bar.baz", {"a": "1"})),
        ("foo.bar.baz?a=1", {"a": "2"}, ("foo.bar.baz", {"a": "2"})),
        ("instance.index?a=1&b=1&b=2&c=3", {}, ("instance.index", {"a": "1", "b": "2", "c": "3"})),
    ],
)
def test_parse_redirect_params(redirect_url, kwargs, expected):
    assert parse_redirect_params(redirect_url, **kwargs) == expected


@pytest.mark.parametrize(
    ("encoded", "expected"),
    [
        ("0", 0),
        ("1", 1),
        ("a", 10),
        ("z", 35),
        ("10", 36),  # 1*36^1 + 0*36^0 = 36
        ("1a", 46),  # 1*36^1 + 10*36^0 = 36 + 10 = 46
        ("ab", 371),  # 10*36^1 + 11*36^0 = 360 + 11 = 371
        ("100", 1296),  # 1*36^2 + 0*36^1 + 0*36^0 = 1296
        ("zzz", 46655),  # 35*36^2 + 35*36^1 + 35*36^0 = 45360 + 1260 + 35 = 46655
    ],
)
def test_base36_decode_basic(encoded, expected):
    """Test basic Base36 decoding functionality"""
    assert Base36Handler.decode(encoded) == expected


@pytest.mark.parametrize(
    ("num", "alphabet"),
    [
        (0, Base36Handler.BASE36),
        (1, Base36Handler.BASE36),
        (10, Base36Handler.BASE36),
        (35, Base36Handler.BASE36),
        (36, Base36Handler.BASE36),
        (371, Base36Handler.BASE36),
        (1296, Base36Handler.BASE36),
        (46655, Base36Handler.BASE36),
        # Test with custom alphabet
        (10, "0123456789"),  # Decimal
        (15, "0123456789abcdef"),  # Hexadecimal
    ],
)
def test_base36_encode_decode_roundtrip(num, alphabet):
    """Test that encode and decode are inverse operations"""
    encoded = Base36Handler.encode(num, alphabet)
    decoded = Base36Handler.decode(encoded, alphabet)
    assert decoded == num
