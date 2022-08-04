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
import os
import random
import time
import uuid

import pytest
import redis

from blue_krill.redis_tools.messaging import StreamChannel, StreamChannelSubscriber
from blue_krill.redis_tools.sentinel import SentinelBackend
from tests.utils import generate_random_string


@pytest.fixture
def redis_db():
    """
    Return a Redis client object configured from the given URL

    For example::

        redis://[[username]:[password]]@localhost:6379/0
        rediss://[[username]:[password]]@localhost:6379/0
        unix://[[username]:[password]]@/path/to/socket.sock?db=0
    """
    if "REDIS_URL" not in os.environ or not os.environ["REDIS_URL"]:
        raise pytest.skip("MISSING REDIS_URL")
    return redis.Redis.from_url(os.environ["REDIS_URL"])


@pytest.fixture
def rand_key():
    return f'foo{generate_random_string(length=6)}'


@pytest.fixture
def redis_sentinel_db(rand_key):
    REDIS_URL = os.environ.get('REDIS_SENTINEL_URL')
    SENTINEL_MASTER_NAME = os.environ.get('SENTINEL_MASTER_NAME')
    SENTINEL_PASSWORD = os.environ.get('SENTINEL_PASSWORD')

    if REDIS_URL and SENTINEL_MASTER_NAME:
        sentinel_kwargs = {'password': SENTINEL_PASSWORD} if SENTINEL_PASSWORD else {}
        client = SentinelBackend(REDIS_URL, SENTINEL_MASTER_NAME, sentinel_kwargs).client
        client.set(rand_key, 'bar')
        yield client
        client.delete(rand_key)

    raise pytest.skip('MISSING REDIS SENTINEL CONFIG IN ENVIRONMENT VARIABLES')


@pytest.fixture
def channel_id():
    return uuid.uuid4().hex


class TestMessageChannel:
    @pytest.fixture(autouse=True)
    def setUp(self, redis_db, channel_id):
        self.redis_db = redis_db
        self.channel_id = channel_id

    def producer(self, batch=4, wait=0.25):
        channel = StreamChannel(self.channel_id, self.redis_db)
        channel.initialize()
        for i in range(batch):
            channel.publish_msg(message='Hello, I am %s.' % (i + 1))
            time.sleep(wait)
        channel.close()

    def test_normal(self):
        channel = StreamChannel(self.channel_id, self.redis_db)
        subscriber = StreamChannelSubscriber(self.channel_id, self.redis_db)
        channel.initialize()
        for i in range(10):
            channel.publish_msg(message='Hello, I am %s.' % (i + 1))

        assert len(subscriber.get_history_events()) == 10
        assert len(subscriber.get_history_events(last_event_id=7)) == 4
        channel.destroy()

    def test_consumer_concurrent(self):
        import threading

        batch = 4

        def consumer():
            subscriber = StreamChannelSubscriber(self.channel_id, self.redis_db)
            events = list(subscriber.get_events())
            assert len(events) == batch

        t1 = threading.Thread(target=self.producer, args=(batch,))
        t2 = threading.Thread(target=consumer)
        for t in [t1, t2]:
            t.start()
        for t in [t1, t2]:
            t.join()

    def test_consumer_start_late(self):
        import threading

        batch = 4

        def consumer():
            # Wait for a long time after producer closed
            time.sleep(1.5)

            subscriber = StreamChannelSubscriber(self.channel_id, self.redis_db)
            events = list(subscriber.get_events())
            assert len(events) == batch

        t1 = threading.Thread(target=self.producer, args=(batch,))
        t2 = threading.Thread(target=consumer)
        for t in [t1, t2]:
            t.start()
        for t in [t1, t2]:
            t.join()

    def test_consumer_start_middle(self):
        import threading

        batch = 4

        def consumer():
            # Wait for a long time after producer closed
            time.sleep(0.7)

            subscriber = StreamChannelSubscriber(self.channel_id, self.redis_db)
            events = list(subscriber.get_events())
            assert len(events) == batch

        t1 = threading.Thread(target=self.producer, args=(batch,))
        t2 = threading.Thread(target=consumer)
        for t in [t1, t2]:
            t.start()
        for t in [t1, t2]:
            t.join()

    def test_consumer_with_last_event_id(self):
        import threading

        batch = 4

        def consumer():
            # Wait for a long time after producer closed
            time.sleep(1.2)

            subscriber = StreamChannelSubscriber(self.channel_id, self.redis_db)
            events = list(subscriber.get_events(last_event_id=2))
            assert len(events) == (batch - 1)

        t1 = threading.Thread(target=self.producer, args=(batch,))
        t2 = threading.Thread(target=consumer)
        for t in [t1, t2]:
            t.start()
        for t in [t1, t2]:
            t.join()

    def test_consumer_start_too_early(self):
        import threading

        batch = 4

        def consumer():
            subscriber = StreamChannelSubscriber(self.channel_id, self.redis_db)
            events = list(subscriber.get_events())
            assert len(events) == batch

        t1 = threading.Thread(target=self.producer, args=(batch,))
        t2 = threading.Thread(target=consumer)
        t2.start()
        time.sleep(1)
        t1.start()
        for t in [t1, t2]:
            t.join()


class TestSentinel:
    @pytest.fixture
    def sentinel_hosts(self):
        return [generate_random_string(10) for _ in range(2)]

    @pytest.fixture
    def sentinel_port(self):
        return random.randint(0, 65535)

    @pytest.fixture
    def sentinel_password(self):
        return generate_random_string(10)

    @pytest.fixture
    def redis_password(self):
        return generate_random_string(10)

    @pytest.fixture
    def redis_db(self):
        return random.randint(0, 15)

    @pytest.fixture
    def master_name(self):
        return generate_random_string(10)

    @pytest.fixture
    def sentinel_url(self, sentinel_hosts, sentinel_port, redis_password, redis_db):
        sentinel_hosts = [f'sentinel://:{redis_password}@{host}:{sentinel_port}/{redis_db}' for host in sentinel_hosts]
        return ';'.join(sentinel_hosts)

    @pytest.fixture
    def invalid_sentinel_urls(self):
        return ['http://', 'sentinel://;http:', 'sentinel://;', 'sentine1://']

    def test_create_sentinel_backend(
        self, sentinel_url, master_name, sentinel_hosts, sentinel_password, sentinel_port, redis_password, redis_db
    ):
        sentinel_kwargs = {'password': sentinel_password}
        backend = SentinelBackend(sentinel_url, master_name, sentinel_kwargs)

        assert backend.hosts == [{'host': h, 'port': sentinel_port} for h in sentinel_hosts]
        assert backend.sentinel_kwargs == sentinel_kwargs
        assert backend.master_name == master_name
        assert backend.password == redis_password
        assert backend.db == redis_db

    def test_invalid_url_backend(self, invalid_sentinel_urls, master_name, sentinel_password):
        """测试不合法的 sentinel url 输入"""
        sentinel_kwargs = {'password': sentinel_password}
        for invalid_url in invalid_sentinel_urls:
            with pytest.raises(ValueError):
                SentinelBackend(invalid_url, master_name, sentinel_kwargs)

    def test_backend_client(self, redis_sentinel_db, rand_key):
        assert redis_sentinel_db.get(rand_key) == b'bar'
