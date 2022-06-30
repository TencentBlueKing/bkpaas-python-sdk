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

import pytest

from blue_krill.connections.ha_algorithm import BasicHAAlgorithm
from blue_krill.connections.ha_endpoint_pool import Endpoint, HAEndpointPool


@pytest.fixture
def ep_pool() -> HAEndpointPool:
    fake_list = [f"fake_ep_{n}" for n in range(5)]
    return HAEndpointPool(fake_list)


class TestEndpointPoolSucceedAndFail:
    def test_success_and_elect(self, ep_pool: HAEndpointPool):
        ep_pool.succeed()
        ep = ep_pool.get_endpoint()
        assert ep.success_count == 1
        assert ep.score == 101

        ep_pool.elect()
        assert ep_pool.get_endpoint() == ep

    def test_success_with_score(self, ep_pool: HAEndpointPool):
        ep_pool.succeed(10)
        assert ep_pool.get_endpoint().score == 110

    def test_unhealthy(self, ep_pool: HAEndpointPool):
        ep = ep_pool.get_endpoint()
        for _ in range(ep_pool.algorithm.unhealthy_max_failed):
            ep_pool.fail()
        assert ep.is_unhealthy() is True

    def test_fail_and_elect(self, ep_pool: HAEndpointPool):
        ep_pool.fail()
        ep = ep_pool.get_endpoint()
        assert ep.failure_count == 1

        ep_pool.elect()
        assert ep_pool.get_endpoint() != ep, "Should return a new Endpoint"
        assert ep_pool.get_endpoint().score > ep.score

    def test_fail_with_score(self, ep_pool: HAEndpointPool):
        ep_pool.fail(10)
        assert ep_pool.get_endpoint().score == 90

    def test_fail_and_set_unhealthy(self, ep_pool: HAEndpointPool):
        assert len(ep_pool.list_healthy()) == 5
        for _ in range(ep_pool.algorithm.unhealthy_max_failed + 1):
            ep_pool.fail()
        assert len(ep_pool.list_healthy()) == 4

    def test_fail_and_recover(self, ep_pool: HAEndpointPool):
        class AlwaysHealthy(BasicHAAlgorithm):
            def should_recover(self, endpoint: 'Endpoint') -> bool:
                return True

        ep_pool = HAEndpointPool([f"fake_ep_{n}" for n in range(5)], algorithm=AlwaysHealthy())
        assert len(ep_pool.list_healthy()) == 5
        for _ in range(ep_pool.algorithm.unhealthy_max_failed + 1):
            ep_pool.fail()
        assert len(ep_pool.list_healthy()) == 4

        # All unhealthy endpoints should be recovered due to the algorithm
        ep_pool.elect()
        assert len(ep_pool.list_healthy()) == 5


class TestEndpointPoolElect:
    def test_manually(self, ep_pool: HAEndpointPool):
        the_ep = ep_pool.get_endpoint()
        the_ep.fail()
        ep_pool.elect()
        assert ep_pool.get_endpoint() != the_ep

        ep_pool.elect(the_ep)
        assert ep_pool.get_endpoint() == the_ep


class TestEndpointPoolOnce:
    def test_sequential_calls(self, ep_pool):
        with ep_pool.once():
            # use fake item to do something
            raise ValueError("unittest error")

        assert ep_pool.get_endpoint().failure_count == 1

        with ep_pool.once():
            # A new endpoint should be elected
            pass

        ep = ep_pool.get_endpoint()
        assert ep.failure_count == 0
        assert ep.success_count == 1


class TestEndpoint:
    def test_success(self):
        ep = Endpoint('foo')
        ep.succeed()
        assert ep.success_count == 1

    def test_success_exceeds_maximum(self):
        ep = Endpoint('foo')
        ep.succeed(ep.max_score * 5)

        assert ep.success_count == 1
        assert ep.score == ep.max_score

    def test_fail(self):
        ep = Endpoint('foo')
        ep.fail()
        assert ep.failure_count == 1

    def test_fail_exceeds_minimal(self):
        ep = Endpoint('foo')
        ep.fail((ep.max_score - ep.min_score) * 5)

        assert ep.failure_count == 1
        assert ep.score == ep.min_score

    def test_health_and_unhealthy(self):
        ep = Endpoint('foo')
        assert ep.is_unhealthy() is False

        ep.fail()
        ep.set_unhealthy()
        assert ep.is_unhealthy() is True

        ep.set_healthy()
        assert ep.is_unhealthy() is False
        assert ep.failure_count == 0


class TestBasicHAAlgorithm:
    def test_is_unhealthy(self):
        algo = BasicHAAlgorithm()
        ep = Endpoint('foo')
        assert algo.is_unhealthy(ep) is False

        for _ in range(algo.unhealthy_max_failed + 1):
            ep.fail()
        assert algo.is_unhealthy(ep) is True

    def test_should_recover(self):
        algo = BasicHAAlgorithm()
        ep = Endpoint('foo')
        assert algo.should_recover(ep) is False

        ep.unhealthy_at = datetime.datetime.now() - datetime.timedelta(days=1)
        assert algo.should_recover(ep) is True
