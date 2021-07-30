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
import random
import socket

import pytest

from blue_krill.monitoring.probe.tcp import InternetAddress, TCPProbe


class TestTCPProbe:
    @pytest.fixture()
    def server_address(self):
        return InternetAddress(host="localhost", port=random.randint(30000, 60000))

    @pytest.fixture()
    def tcp_server(self, server_address):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(server_address)
        # only support 1 client.
        server.listen(1)
        yield
        server.close()

    @pytest.fixture()
    def prober(self, server_address):
        class SomeTCPProbe(TCPProbe):
            timeout = 5
            address = server_address

        return SomeTCPProbe()

    def test_success(self, tcp_server, prober):
        issues = prober.diagnose()
        assert len(issues) == 0

    def test_busy(self, tcp_server, prober):
        prober.diagnose()
        issues = prober.diagnose()
        assert len(issues) == 1
        issue = issues[0]
        assert issue.fatal
        assert issue.description == "Unknown Exception<ConnectionRefusedError>, detail: [Errno 61] Connection refused"

    def test_no_server(self, prober):
        issues = prober.diagnose()
        assert len(issues) == 1
        issue = issues[0]
        assert issue.fatal
        assert issue.description == "Unknown Exception<ConnectionRefusedError>, detail: [Errno 61] Connection refused"
