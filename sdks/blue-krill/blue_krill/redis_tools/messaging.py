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
import json
import logging
import time

from blue_krill.encoding import force_text

logger = logging.getLogger(__name__)


class StreamChannel(object):
    """A simple stream channel implemention"""

    default_expires_seconds = 3600 * 24

    def __init__(self, channel_id, redis_db=None, expires_seconds=None):
        self.channel_id = channel_id
        self.keys = KeyManager(channel_id)
        self.redis_db = redis_db
        self.expires_seconds = expires_seconds or self.default_expires_seconds

    def initialize(self):
        """Initialize channel"""
        if self.redis_db.exists(self.keys.counter):
            return

        # Always update state first
        self.redis_db.set(self.keys.state, 'open')
        self.publish('init')

        # Set expires
        pipe = self.redis_db.pipeline()
        for key in self.keys.entities():
            pipe.expire(key, self.expires_seconds)
        pipe.execute()

    def publish_msg(self, message):
        self.publish('msg', data=message)

    def publish(self, event, data=''):
        index = self.redis_db.incr(self.keys.counter)
        payload = {'id': index, 'event': event, 'data': data}
        self.redis_db.rpush(self.keys.history, json.dumps(payload))
        self.redis_db.publish(self.keys.channel, json.dumps(payload))

    def close(self):
        self.redis_db.set(self.keys.state, 'closed', self.expires_seconds)
        self.publish('close')

    def destroy(self):
        """Destory this channel, every history events will be deleted!"""
        pipe = self.redis_db.pipeline()
        for key in self.keys.entities():
            pipe.delete(key)
        pipe.execute()

    def __str__(self):
        return 'StreamChannel: {}'.format(self.channel_id)


class StreamChannelSubscriber(object):
    """Subscriber for StreamChannel"""

    def __init__(self, channel_id, redis_db=None):
        self.channel_id = channel_id
        self.keys = KeyManager(channel_id)
        self.redis_db = redis_db

        self.sub_pipe = self.redis_db.pubsub(ignore_subscribe_messages=True)
        self.sub_pipe.subscribe(self.keys.channel)

        self.update_channel_state()

    def get_channel_state(self):
        return self._channel_state

    def update_channel_state(self):
        self._channel_state = self.read_channel_state()

    def read_channel_state(self):
        state = self.redis_db.get(self.keys.state)
        state = force_text(state)
        if state is None:
            return 'none'
        elif state == 'open':
            return 'open'
        elif state == 'closed':
            return 'closed'
        return 'unknown'

    def is_closed(self):
        return self.get_channel_state() == 'closed'

    def get_history_events(self, last_event_id=0, ignore_special=True):
        """Get history events

        :param int last_event_id: If given, result will start from last_event_id
        """
        results = []
        for item in self.redis_db.lrange(self.keys.history, last_event_id, -1):
            event = json.loads(item)
            # Update Channel status if event is special
            if self.is_special_event(event):
                self.update_channel_state()
            if ignore_special and self.is_special_event(event):
                continue
            results.append(event)
        return results

    def get_events(self, last_event_id=0, wait=0.05, ignore_special=True):
        """Get all history events and follow new one.

        :param int last_event_id: Ignore every events whose id is lower than this
        :param int wait: Wait for seconds for every cycle
        """
        # TODO: If a channel is not open for a long time, raise an exception
        events = self.get_history_events(last_event_id=last_event_id, ignore_special=ignore_special)
        for event in events:
            yield event

        max_event_id = events[-1]['id'] if events else last_event_id
        while True:
            if self.is_closed():
                break
            event = self.get_event(block=False)
            # Be nice to your system, sleep for a while
            if not event:
                time.sleep(wait)
                continue
            # Ignore event that already fetched from history events
            if event['id'] <= max_event_id:
                continue
            if ignore_special and self.is_special_event(event):
                continue
            yield event

    def get_event(self, block=False):
        """Get event from subscribe

        :param block bool: if True, will use .listen method to do a sync read
        """
        if block:
            _data = next(self.sub_pipe.listen())
        else:
            _data = self.sub_pipe.get_message()
        if not _data:
            return

        data = json.loads(_data['data'])

        # Update Channel status if event is special
        if self.is_special_event(data):
            self.update_channel_state()
        return data

    def is_special_event(self, event):
        return event['event'] in ('init', 'close')

    def close(self):
        self.sub_pipe.close()

    def __str__(self):
        return 'StreamChannelSubscriber: {}'.format(self.channel_id)


class KeyManager(object):
    """Redis key manager for channel"""

    default_key_prefix = 'p3::'

    def __init__(self, channel_id, prefix=None):
        prefix = prefix or self.default_key_prefix
        self.state = '{}evtch::{}::sta'.format(prefix, channel_id)
        self.counter = '{}evtch::{}::cnt'.format(prefix, channel_id)
        self.history = '{}evtch::{}::his'.format(prefix, channel_id)
        self.channel = '{}evtch::{}::cha'.format(prefix, channel_id)

    def entities(self):
        return [self.state, self.counter, self.history]
