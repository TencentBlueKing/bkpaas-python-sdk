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
import unittest

from blue_krill.connections.ha_algorithm import BasicHAAlgorithm
from blue_krill.connections.ha_endpoint_pool import Endpoint, HAEndpointPool


class TestEndpointPool(unittest.TestCase):
    def setUp(self) -> None:
        fake_list = [f"fake{x}" for x in range(5)]
        self.pool = HAEndpointPool.from_list(fake_list)  # type: ignore

    def test_fail(self):
        self.pool.fail()

        fake_one_score = self.pool.active_endpoint.score
        assert self.pool.active_endpoint.failure_count == 1

        self.pool.elect()
        assert fake_one_score < self.pool.active_endpoint.score

    def test_fail_custom_score_delta(self):
        self.pool.fail(score_delta=10)
        assert self.pool.active_endpoint.score == 90

    def test_success(self):
        self.pool.succeed()

        assert self.pool.active_endpoint.success_count == 1
        assert self.pool.active_endpoint.score == 101

        self.pool.succeed(score_delta=10)
        assert self.pool.active_endpoint.score == 111

    def test_isolate(self):
        for _ in range(self.pool.algorithm.failure_threshold):
            self.pool.fail()

        assert len(self.pool.data) == 4

    def test_get_endpoint(self):
        with self.pool.get_endpoint(auto_reelect=False):
            # use fake item to do something
            raise ValueError("unittest error")

        assert self.pool.active.failure_count == 1

        self.pool.elect()
        with self.pool.get_endpoint(auto_reelect=False):
            # nothing happen
            pass

        assert self.pool.active_endpoint.failure_count == 0
        assert self.pool.active_endpoint.success_count == 1

    def test_get_endpoint_auto_reelect(self):
        with self.pool.get_endpoint():
            # use fake item to do something
            raise ValueError("unittest error")

        assert self.pool.active_endpoint.failure_count == 0

    def test_custom_isolate(self):
        def custom_isolate(endpoint):
            return endpoint.failure_count > 0

        self.pool.fail(isolate_method=custom_isolate)

        assert len(self.pool.data) == 4

    def test_custom_elect(self):
        def custom_isolate(endpoints):
            return endpoints[0]

        self.pool.elect(method=custom_isolate)

        # fake0 has lower score now
        self.pool.fail()
        self.pool.fail()

        # still return first one
        assert self.pool.active_endpoint.raw == "fake0"

    def test_recover_normal_logic(self):
        self.pool.elect()

        # trying to isolate
        for _ in range(self.pool.algorithm.failure_threshold):
            self.pool.fail()

        # make sure endpoint already been recovered
        self.pool.recover()
        assert len(self.pool) == len(self.pool._all_pool)

    def test_custom_recover_method(self):
        self.pool.elect()

        # trying to isolate
        for _ in range(self.pool.algorithm.failure_threshold):
            self.pool.fail()

        def never_recover(endpoint):
            return False

        self.pool.recover(method=never_recover)
        assert len(self.pool._all_pool) - len(self.pool) == 1


class TestBasicHAAlgorithm(unittest.TestCase):
    def setUp(self) -> None:
        self.algo = BasicHAAlgorithm()

        fake_list = [f"fake{x}" for x in range(5)]
        self.endpoints = [Endpoint(raw=x) for x in fake_list]

    def test_find_tops(self):
        with self.assertRaises(ValueError):
            self.algo.find_best_endpoint([])

        self.endpoints[0].succeed(10)
        self.endpoints[1].succeed(20)
        self.endpoints[2].succeed(20)

        tops = self.algo._find_tops(self.endpoints)
        assert len(tops) == 2
        assert tops[0].score == 120


class TestEndpoint(unittest.TestCase):
    def setUp(self) -> None:
        raw = {'fake': "it's me"}
        self.endpoint = Endpoint(raw)

    def test_normal_success(self):
        self.endpoint.succeed()
        assert self.endpoint.success_count == 1

    def test_beyond_max_success(self):
        self.endpoint.succeed(self.endpoint.max_score * 5)

        assert self.endpoint.success_count == 1
        assert self.endpoint.score == self.endpoint.max_score

    def test_normal_fail(self):
        self.endpoint.fail()
        assert self.endpoint.failure_count == 1

    def test_beyond_min_fail(self):
        self.endpoint.fail((self.endpoint.max_score - self.endpoint.min_score) * 5)

        assert self.endpoint.failure_count == 1
        assert self.endpoint.score == self.endpoint.min_score


if __name__ == "__main__":
    unittest.main()
