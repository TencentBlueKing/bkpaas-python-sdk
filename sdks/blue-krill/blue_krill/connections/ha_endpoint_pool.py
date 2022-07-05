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
import datetime
import logging
import random
from contextlib import contextmanager
from dataclasses import dataclass, field
from operator import attrgetter
from threading import RLock
from typing import Any, Generic, Iterable, List, Optional, Tuple, Type, TypeVar

from .exceptions import NoEndpointAvailable
from .ha_algorithm import BasicHAAlgorithm

logger = logging.getLogger(__name__)

T = TypeVar('T')

SUCCESS_SCORE_DELTA = 1
FAILURE_SCORE_DELTA = 50


class HAEndpointPool(Generic[T]):
    """A container type which holds a collection of endpoints, provides HA-related functions,
    e.g. fail(), elect() ect.

    :param items: raw items, each will be bound with an Endpoint object
    :param algorithm: HA Algorithm object, default value: `BasicHAAlgorithm`
    """

    active_endpoint: 'Endpoint'

    def __init__(self, items: Iterable[T], algorithm: 'BasicHAAlgorithm' = BasicHAAlgorithm()):
        self._rlock = RLock()
        self.algorithm = algorithm
        self.endpoints: 'List[Endpoint]' = []

        # Initialize endpoints and start first election
        for item in items:
            self.add(item)
        self.elect()

    def add(self, item: T):
        """Add an endpoint object"""
        self.endpoints.append(Endpoint(raw=item))

    def elect(self, endpoint: 'Optional[Endpoint]' = None):
        """Set `self.active_endpoint` to the best endpoint, it should be the healthy one with
        highest score.

        :param endpoint: Set given Endpoint directly, ignore any algorithms
        """
        with self._rlock:
            # Try to recover unhealthy endpoints
            for ep in self.endpoints:
                if self.algorithm.should_recover(ep):
                    ep.set_healthy()

            if endpoint:
                self.active_endpoint = endpoint
                return

            # Get endpoints with maximum score
            eps = sorted(self.list_healthy(), key=attrgetter('score'), reverse=True)
            if not eps:
                raise NoEndpointAvailable('No healthy endpoint')

            best = random.choice([x for x in eps if x.score == eps[0].score])
            self.active_endpoint = best
            logger.debug(f"Election finished, best: {best}")

    def get(self) -> T:
        """Get current active item"""
        return self.active_endpoint.raw

    def get_endpoint(self) -> 'Endpoint':
        """Get current active endpoint object"""
        return self.active_endpoint

    def list_healthy(self) -> 'List[Endpoint]':
        """List all healthy Endpoints"""
        return [ep for ep in self.endpoints if not ep.is_unhealthy()]

    def fail(self, score: int = FAILURE_SCORE_DELTA):
        """Mark current active endpoint as failed"""
        with self._rlock:
            self.active_endpoint.fail(score_delta=score)
            if self.algorithm.is_unhealthy(self.active_endpoint):
                self.active_endpoint.set_unhealthy()

    def succeed(self, score_delta: int = SUCCESS_SCORE_DELTA):
        """Mark current active endpoint as succeeded"""
        with self._rlock:
            self.active_endpoint.succeed(score_delta=score_delta)

    @contextmanager
    def once(self, failure_excs: Tuple[Type[Exception], ...] = ()) -> Any:
        """A simple context manger which updates endpoint's status automatically. Basically it
        marks current endpoint as "succeed" when everything goes smoothly. But when the code raises
        an exception, it will be captured silently and current endpoint will be marked as "failure"
        if the exception was an instance of `failure_excs`, otherwise it will be raised as is.

        :param failure_excs: Exception types which will be captured.
        """
        # Always call elect() when context begins
        self.elect()
        try:
            yield self.get()
        except Exception as e:
            if isinstance(e, failure_excs):
                logger.warning("Got exception: %s, mark the active endpoint %s as failure", e, self.active_endpoint)
                self.fail()
            else:
                raise
        else:
            self.succeed()

    def __repr__(self) -> str:
        return f'HAEndpointPool(active_endpoint={self.active_endpoint!r}, endpoints={self.endpoints!r})'


@dataclass(order=True)
class Endpoint:
    raw: Any = field(compare=False)
    # Avoid some nodes' scores would be extremely high for the long-term stable,
    # causing error switching time too long.
    max_score: int = 150
    min_score: int = -50

    # score could extend for weight
    # NOTE: do not change _score directly, use fail() & success() please
    _score: int = 100
    success_count: int = 0
    failure_count: int = 0

    # When current endpoint was marked as "unhealthy"(not available)
    unhealthy_at: Optional[datetime.datetime] = None

    def __repr__(self):
        return repr(self.raw) + f"-score<{self._score}>"

    def __hash__(self):
        return hash(repr(self))

    @property
    def score(self):
        return self._score

    def fail(self, score_delta: int = 0):
        """
        :param score_delta: delta of score
        :return: no return
        """
        self._update_score(score_delta=score_delta)
        self.failure_count += 1

    def succeed(self, score_delta: int = 0):
        self._update_score(score_delta=score_delta, fail=False)
        self.success_count += 1

    def is_unhealthy(self):
        """Whether current endpoint is unhealthy"""
        return self.unhealthy_at is not None

    def set_unhealthy(self):
        """Set current endpoint as unhealthy"""
        self.unhealthy_at = datetime.datetime.now()

    def set_healthy(self):
        """Set current endpoint as healthy"""
        self.failure_count = 0
        self.unhealthy_at = None

    def _adjust_max_min(self):
        if self._score >= self.max_score:
            self._score = self.max_score
            return

        if self._score <= self.min_score:
            self._score = self.min_score
            return

    def _update_score(self, score_delta: int, fail: bool = True):
        if score_delta < 0:
            raise ValueError("score delta should not be negative")

        if fail:
            self._score -= score_delta
        else:
            self._score += score_delta

        # make sure score will not beyond preset interval
        self._adjust_max_min()
