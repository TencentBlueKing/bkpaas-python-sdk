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
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type

from .decorators import elect_if_no_active_ep, raise_if_no_data, use_algo_as_default
from .exceptions import NoEndpointAvailable
from .ha_algorithm import BasicHAAlgorithm

logger = logging.getLogger(__name__)


@dataclass
class HAEndpointPool:
    """Endpoints pool which own high available features like failOver"""

    # for safety of thread
    _rlock = RLock()

    _active: Optional['Endpoint'] = None
    # all endpoint
    _all_pool: List['Endpoint'] = field(default_factory=list)
    # only include available endpoints
    _pool: List['Endpoint'] = field(default_factory=list)

    algorithm: 'BasicHAAlgorithm' = field(default_factory=BasicHAAlgorithm)

    success_score_delta: int = 1
    failure_score_delta: int = 50

    # initial config for endpoints, only available when add new endpoint by pool
    endpoint_config: Dict = field(default_factory=dict)

    def __len__(self):
        """pool could be treat as available pool"""
        return len(self._pool)

    @classmethod
    def from_list(cls, raw_list: Optional[Iterable]) -> 'HAEndpointPool':
        pool = cls()
        # generator always return True
        raw_list = list(raw_list)
        if not raw_list:
            raise ValueError("raw list can not be empty")

        # TODO: elements in list may be duplicate
        # Q: Why not use set() which is a easy way to deduplicate?
        # A: Raw object may not contain __hash__ (like default dataclass)
        for raw_endpoint in raw_list:
            pool.add(raw_endpoint)
        return pool

    @property
    def data(self) -> List:
        return self._pool

    @property
    def active(self) -> 'Endpoint':
        return self._active

    @property
    def isolated_eps(self) -> List['Endpoint']:
        return list(set(self._all_pool) - set(self._pool))

    def add(self, raw_end_point: Any):
        """receive any type, mount on endpoint"""
        self._all_pool.append(Endpoint(raw=raw_end_point, **self.endpoint_config))
        self._pool.append(Endpoint(raw=raw_end_point, **self.endpoint_config))

    def add_endpoint(self, endpoint: 'Endpoint', available: bool = True):
        """add endpoint directly"""
        self._all_pool.append(endpoint)
        if available:
            self._pool.append(endpoint)

    @elect_if_no_active_ep
    def fail(self, isolate_method: Callable[['Endpoint'], bool] = None, score_delta: int = None):
        """mark active endpoint as failure, and try to scan entire pool for isolating"""
        if not score_delta:
            score_delta = self.failure_score_delta

        with self._rlock:
            self._active.fail(score_delta=score_delta)
            # only isolate when fail
            self.try_to_isolate(method=isolate_method)

    @elect_if_no_active_ep
    def succeed(self, score_delta: int = None):
        if not score_delta:
            score_delta = self.success_score_delta

        with self._rlock:
            self._active.succeed(score_delta=score_delta)

    @use_algo_as_default('should_be_isolated')
    def try_to_isolate(self, method: Callable[['Endpoint'], bool] = None):
        with self._rlock:
            # both copy.copy() and copy.deepcopy() are not thread safe!
            pool_copy = list(self._pool)
            for ep in pool_copy:
                if method(ep):
                    self._pool.remove(ep)

        if not self._pool:
            raise NoEndpointAvailable("no Endpoint available in pool")

    @use_algo_as_default('should_be_recovered')
    def recover(self, method: Callable[['Endpoint'], bool] = None):
        """recover endpoints which is not in self._pool"""
        if not self.isolated_eps:
            return

        with self._rlock:
            for ep in self.isolated_eps:
                # put back if should be recovered
                if method(ep):
                    self._pool.append(ep)

    def pick(self, elect_method: Callable[[List['Endpoint']], 'Endpoint'] = None) -> Any:
        """elect and pick raw data of active endpoint"""
        self.elect(elect_method)
        return self._active.raw

    @raise_if_no_data
    @use_algo_as_default('find_best_endpoint')
    def elect(self, method: Callable[[List['Endpoint']], 'Endpoint'] = None):
        """elect by elect_method and set active"""
        elected = method(self._pool)
        with self._rlock:
            self._active = elected
            logger.info(f"elect {elected.raw} as new active endpoint with score<{elected.score}>")

    @contextmanager
    def get_endpoint(
        self,
        auto_reelect: bool = True,
        auto_recover: bool = True,
        isolate_method: Callable[['Endpoint'], bool] = None,
        elect_method: Callable[[List['Endpoint']], 'Endpoint'] = None,
        recover_method: Callable[['Endpoint'], bool] = None,
        exempt_exceptions: Tuple[Type[Exception], ...] = (),
    ) -> Any:
        """
        use context manager to simplify failOver process

        :param auto_reelect: if auto reelect
        :param isolate_method: custom isolate method
        :param elect_method: custom elect method
        :param recover_method: custom recover method
        :param exempt_exceptions: exceptions which should not be mark as failure
        """
        try:
            if not self._active:
                if auto_recover:
                    self.recover(method=recover_method)

                self.elect(method=elect_method)

            yield self._active.raw
        except Exception as e:  # pylint: disable=broad-except
            if isinstance(e, exempt_exceptions):
                logger.exception("endpoints pool got exception, " "but raising anyway according to upper caller")
                raise

            logger.warning(
                f"endpoints pool got exception: {e}, " f"the active endpoint {self._active} will be mark as failure"
            )
            self.fail(isolate_method)
            if auto_reelect:
                if auto_recover:
                    self.recover(method=recover_method)

                self.elect(method=elect_method)
        else:
            self.succeed()


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
    # for recovery
    last_failure_time: datetime.datetime = None

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
        self.last_failure_time = datetime.datetime.now()
        self.failure_count += 1

    def succeed(self, score_delta: int = 0):
        self._update_score(score_delta=score_delta, fail=False)
        self.success_count += 1

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
