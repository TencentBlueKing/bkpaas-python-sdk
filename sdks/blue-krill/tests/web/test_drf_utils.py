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
from rest_framework.exceptions import ErrorDetail, ValidationError

from blue_krill.web.drf_utils import stringify_validation_error


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        # Simple structure
        (ValidationError("foo"), ["foo"]),
        (ValidationError([ErrorDetail("foo1"), ErrorDetail("foo2")]), ["foo1", "foo2"]),
        (ValidationError({"foo": ErrorDetail("err")}), ["foo: err"]),
        # Nested structure
        (ValidationError({"foo": [ErrorDetail("err1"), ErrorDetail("err2")]}), ["foo: err1", "foo: err2"]),
        (
            ValidationError({"foo": {"bar": [ErrorDetail("err1"), ErrorDetail("err2")]}}),
            ["foo.bar: err1", "foo.bar: err2"],
        ),
        (
            ValidationError({"foo": {"bar1": [ErrorDetail("err1"), ErrorDetail("err2")], "bar2": {"bar3": "err"}}}),
            ["foo.bar1: err1", "foo.bar1: err2", "foo.bar2.bar3: err"],
        ),
    ],
)
def test_stringify_validation_error(error, expected):
    assert stringify_validation_error(error) == expected
