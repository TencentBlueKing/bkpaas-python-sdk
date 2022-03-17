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
import time
import uuid
import pytest

import redis

from blue_krill.redis_tools.messaging import StreamChannel, StreamChannelSubscriber


@pytest.fixture
def redis_db():
    if "REDIS_PORT" not in os.environ:
        raise pytest.skip("MISSING REDIS_PORT")
    return redis.Redis(port=int(os.environ["REDIS_PORT"]), password=os.getenv("REDIS_PASSWORD", None))


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
        [t.start() for t in [t1, t2]]
        [t.join() for t in [t1, t2]]

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
        [t.start() for t in [t1, t2]]
        [t.join() for t in [t1, t2]]

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
        [t.start() for t in [t1, t2]]
        [t.join() for t in [t1, t2]]

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
        [t.start() for t in [t1, t2]]
        [t.join() for t in [t1, t2]]

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
        [t.join() for t in [t1, t2]]
