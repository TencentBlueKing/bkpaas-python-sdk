# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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

from blue_krill.text import desensitize_url, remove_prefix, remove_suffix


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "scheme://username:password@hostname:6666/path/?foo=bar",
            "scheme://username:********@hostname:6666/path/?foo=bar",
        )
    ],
)
def test_desensitize_url(url, expected):
    assert desensitize_url(url) == expected


@pytest.mark.parametrize(
    ("input_", "suffix", "output"),
    [
        ("foo", "bar", "foo"),
        ("foobar", "foo", "foobar"),
        ("foobar", "bar", "foo"),
        ("foobar", "foobar", ""),
    ],
)
def test_remove_suffix(input_, suffix, output):
    assert remove_suffix(input_, suffix) == output


@pytest.mark.parametrize(
    ("input_", "prefix", "output"),
    [
        ("foo", "foo", ""),
        ("foo", "bar", "foo"),
        ("foobar", "foo", "bar"),
        ("foobar", "bar", "foobar"),
        ("foobar", "foobar", ""),
    ],
)
def test_remove_prefix(input_, prefix, output):
    assert remove_prefix(input_, prefix) == output
