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

from blue_krill.monitoring.probe.redis import RedisProbe, RedisSentinelProbe
from tests.utils import generate_random_string


@pytest.fixture
def password():
    return generate_random_string()


class TestRedisProbe:
    def test_password_not_logged(self, password, caplog):
        class Probe(RedisProbe):
            name = "dummy"
            redis_url = f"redis://:{password}@localhost:6379/0"

        with mock.patch.object(redis.Redis, "from_url", side_effect=redis.ConnectionError("refused")):
            issues = Probe().diagnose()

        assert issues
        assert "localhost:6379" in caplog.text
        assert password not in caplog.text

    @pytest.mark.parametrize(
        "redis_url",
        [
            "redis://:{password}@localhost:99999/0",
            "redis://:{password}@localhost:6379x/0",
            "redis://:{password}@:6379/0",
            "redis://localhost:6379/0?password={password}",
            "redis://:ab#{password}@localhost:6379/0",
            "redis://:ab/{password}@localhost:6379/0",
            "redis://:ab?{password}@localhost:6379/0",
            "redis://:ab@{password}/cd@localhost:6379/0",
            "redis://:ab@{password}#cd@localhost:6379/0",
            "redis://:ab@{password}?cd@localhost:6379/0",
        ],
    )
    def test_malformed_url(self, password, caplog, redis_url):
        class Probe(RedisProbe):
            name = "dummy"

        Probe.redis_url = redis_url.format(password=password)
        with mock.patch.object(redis.Redis, "from_url", side_effect=redis.ConnectionError("refused")):
            issues = Probe().diagnose()

        assert len(issues) == 1
        assert issues[0].fatal
        assert password not in caplog.text

    @pytest.mark.parametrize("redis_url", [None, 6379, b"redis://localhost:6379/0"])
    def test_non_string_url(self, caplog, redis_url):
        class Probe(RedisProbe):
            name = "dummy"

        Probe.redis_url = redis_url
        issues = Probe().diagnose()

        assert len(issues) == 1
        assert issues[0].fatal
        assert "<unparsable url>" in caplog.text

    @pytest.mark.parametrize(
        "redis_url",
        [
            "redis://:ab;{password};cd@localhost:6379/0",
            "redis://:12345;{password}@localhost:6379/0",
            "redis://:ab@{password};cd@localhost:6379/0",
        ],
    )
    def test_semicolon_in_password(self, password, caplog, redis_url):
        class Probe(RedisProbe):
            name = "dummy"

        Probe.redis_url = redis_url.format(password=password)
        with mock.patch.object(redis.Redis, "from_url", side_effect=redis.ConnectionError("refused")):
            Probe().diagnose()

        assert "redis://localhost:6379/0" in caplog.text
        assert password not in caplog.text
        assert "12345" not in caplog.text


class TestRedisSentinelProbe:
    def test_password_not_logged(self, password, caplog):
        another_password = generate_random_string()

        class Probe(RedisSentinelProbe):
            name = "dummy"
            redis_url = f"sentinel://:{password}@127.0.0.1:26347/0;sentinel://:{another_password}@127.0.0.2:26347/0"
            master_name = "mymaster"
            sentinel_kwargs = {}

        with mock.patch(
            "blue_krill.monitoring.probe.redis.SentinelBackend", side_effect=redis.ConnectionError("refused")
        ):
            issues = Probe().diagnose()

        assert issues
        assert "127.0.0.1:26347" in caplog.text
        assert "127.0.0.2:26347" in caplog.text
        assert password not in caplog.text
        assert another_password not in caplog.text

    @pytest.mark.parametrize(
        "redis_url",
        [
            "sentinel://:{password}@localhost:6379x/0",
            "sentinel://:{password}@localhost:99999/0;sentinel://:{password}@127.0.0.2:26347/0",
            "sentinel://:ab#{password}@localhost:26347/0",
            "sentinel://:ab@{password}/cd@localhost:26347/0;sentinel://:{password}@127.0.0.2:26347/0",
        ],
    )
    def test_malformed_url(self, password, caplog, redis_url):
        class Probe(RedisSentinelProbe):
            name = "dummy"
            master_name = "mymaster"
            sentinel_kwargs = {}

        Probe.redis_url = redis_url.format(password=password)
        with mock.patch(
            "blue_krill.monitoring.probe.redis.SentinelBackend", side_effect=redis.ConnectionError("refused")
        ):
            issues = Probe().diagnose()

        assert len(issues) == 1
        assert issues[0].fatal
        assert password not in caplog.text

    @pytest.mark.parametrize("redis_url", [None, 26347, b"sentinel://localhost:26347/0"])
    def test_non_string_url(self, caplog, redis_url):
        class Probe(RedisSentinelProbe):
            name = "dummy"
            master_name = "mymaster"
            sentinel_kwargs = {}

        Probe.redis_url = redis_url
        issues = Probe().diagnose()

        assert len(issues) == 1
        assert issues[0].fatal
        assert "<unparsable url>" in caplog.text

    @pytest.mark.parametrize(
        "redis_url",
        [
            "sentinel://:ab;{password};cd@localhost:26347/0",
            "sentinel://:12345;{password}@localhost:26347/0",
            "sentinel://:ab@{password};cd@localhost:26347/0",
        ],
    )
    def test_semicolon_in_password(self, password, caplog, redis_url):
        class Probe(RedisSentinelProbe):
            name = "dummy"
            master_name = "mymaster"
            sentinel_kwargs = {}

        Probe.redis_url = redis_url.format(password=password)
        with mock.patch(
            "blue_krill.monitoring.probe.redis.SentinelBackend", side_effect=redis.ConnectionError("refused")
        ):
            Probe().diagnose()

        # Chunks split by ";" in password can not be redacted reliably
        assert "<unparsable url>" in caplog.text
        assert password not in caplog.text
        assert "12345" not in caplog.text
