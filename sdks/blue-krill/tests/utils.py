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

import importlib.util
import random
from string import ascii_lowercase, digits
from typing import Iterable

import pytest

# 国密算法 (如 SM4) 依赖可选的 tongsuopy, 未安装 blue-krill[gm] 时跳过相关测试
requires_gm = pytest.mark.skipif(
    importlib.util.find_spec("tongsuopy") is None, reason='requires "blue-krill[gm]" to be installed'
)


def generate_random_string(length=30, chars=(ascii_lowercase + digits)):
    """Generates a non-guessable OAuth token

    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = random.SystemRandom()
    return "".join(rand.choice(chars) for x in range(length))


def assert_redacted(text: str, *, secrets: Iterable[str], expected: Iterable[str]):
    """Assert that the text (usually the captured logs) contains all the expected fragments but none of
    the secrets. The expected fragments are required, so that the check never passes vacuously when
    nothing is logged, and the logs are proved to be still helpful for troubleshooting.
    """
    expected = list(expected)
    assert expected, "at least one expected fragment is required"
    for fragment in expected:
        assert fragment in text
    for secret in secrets:
        assert secret not in text
