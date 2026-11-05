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


from unittest import mock

import pytest
import redis

from blue_krill.data_types.url import REDACTED_URL_PLACEHOLDER
from blue_krill.monitoring.probe.redis import RedisProbe, RedisSentinelProbe
from tests.utils import assert_redacted, generate_random_string

# A numeric chunk split by ";" from the password may be mistaken as a port, it must not be logged either
NUMERIC_CHUNK = "12345"


class DummyRedisProbe(RedisProbe):
    name = "dummy"


class DummySentinelProbe(RedisSentinelProbe):
    name = "dummy"
    master_name = "mymaster"
    sentinel_kwargs = {}


@pytest.fixture(autouse=True)
def _connection_refused():
    with mock.patch.object(redis.Redis, "from_url", side_effect=redis.ConnectionError("refused")), mock.patch(
        "blue_krill.monitoring.probe.redis.SentinelBackend", side_effect=redis.ConnectionError("refused")
    ):
        yield


@pytest.fixture
def password():
    return generate_random_string()


def diagnose(probe_cls, redis_url):
    probe = probe_cls()
    probe.redis_url = redis_url
    issues = probe.diagnose()
    assert len(issues) == 1
    assert issues[0].fatal


class TestRedisProbe:
    @pytest.mark.parametrize(
        ("redis_url", "logged_url"),
        [
            ("redis://:{password}@localhost:6379/0", "redis://localhost:6379/0"),
            ("redis://localhost:6379/0?password={password}", "redis://localhost:6379/0"),
            ("redis://:{password}@:6379/0", "redis://:6379/0"),
            # invalid port
            ("redis://:{password}@localhost:99999/0", "redis://localhost:99999/0"),
            ("redis://:{password}@localhost:6379x/0", "redis://localhost:6379x/0"),
            # unescaped separators in password
            ("redis://:ab#{password}@localhost:6379/0", REDACTED_URL_PLACEHOLDER),
            ("redis://:ab/{password}@localhost:6379/0", REDACTED_URL_PLACEHOLDER),
            ("redis://:ab?{password}@localhost:6379/0", REDACTED_URL_PLACEHOLDER),
            ("redis://:ab@{password}/cd@localhost:6379/0", REDACTED_URL_PLACEHOLDER),
            ("redis://:ab@{password}#cd@localhost:6379/0", REDACTED_URL_PLACEHOLDER),
            ("redis://:ab@{password}?cd@localhost:6379/0", REDACTED_URL_PLACEHOLDER),
            # unescaped ";" in password
            ("redis://:ab;{password};cd@localhost:6379/0", "redis://localhost:6379/0"),
            ("redis://:12345;{password}@localhost:6379/0", "redis://localhost:6379/0"),
            ("redis://:ab@{password};cd@localhost:6379/0", "redis://localhost:6379/0"),
        ],
    )
    def test_password_not_logged(self, password, caplog, redis_url, logged_url):
        diagnose(DummyRedisProbe, redis_url.format(password=password))
        assert_redacted(caplog.text, secrets=[password, NUMERIC_CHUNK], expected=[f"connecting to {logged_url}"])


class TestRedisSentinelProbe:
    @pytest.mark.parametrize(
        ("redis_url", "logged_url"),
        [
            (
                "sentinel://:{password}@127.0.0.1:26347/0;sentinel://:{password}@127.0.0.2:26347/0",
                "sentinel://127.0.0.1:26347/0;sentinel://127.0.0.2:26347/0",
            ),
            # invalid port
            ("sentinel://:{password}@localhost:6379x/0", "sentinel://localhost:6379x/0"),
            (
                "sentinel://:{password}@localhost:99999/0;sentinel://:{password}@127.0.0.2:26347/0",
                "sentinel://localhost:99999/0;sentinel://127.0.0.2:26347/0",
            ),
            # unescaped separators in password, the whole url is replaced even if other chunks are well-formed
            ("sentinel://:ab#{password}@localhost:26347/0", REDACTED_URL_PLACEHOLDER),
            (
                "sentinel://:ab@{password}/cd@localhost:26347/0;sentinel://:{password}@127.0.0.2:26347/0",
                REDACTED_URL_PLACEHOLDER,
            ),
            # chunks split by ";" in password can not be redacted reliably
            ("sentinel://:ab;{password};cd@localhost:26347/0", REDACTED_URL_PLACEHOLDER),
            ("sentinel://:12345;{password}@localhost:26347/0", REDACTED_URL_PLACEHOLDER),
            ("sentinel://:ab@{password};cd@localhost:26347/0", REDACTED_URL_PLACEHOLDER),
        ],
    )
    def test_password_not_logged(self, password, caplog, redis_url, logged_url):
        diagnose(DummySentinelProbe, redis_url.format(password=password))
        assert_redacted(
            caplog.text,
            secrets=[password, NUMERIC_CHUNK],
            expected=[f"connecting to {logged_url}, sentinel master_name is mymaster"],
        )


@pytest.mark.parametrize("probe_cls", [DummyRedisProbe, DummySentinelProbe])
@pytest.mark.parametrize("redis_url", [None, 6379, b"redis://localhost:6379/0"])
def test_non_string_url(caplog, probe_cls, redis_url):
    diagnose(probe_cls, redis_url)
    assert f"connecting to {REDACTED_URL_PLACEHOLDER}" in caplog.text
