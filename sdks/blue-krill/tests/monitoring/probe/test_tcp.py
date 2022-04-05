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
import socket
import threading
import time
from socketserver import StreamRequestHandler, TCPServer

import pytest

from blue_krill.monitoring.probe.tcp import InternetAddress, TCPProbe


@pytest.fixture
def usable_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


@pytest.fixture
def tcpd(usable_port):
    server_address = InternetAddress(host="localhost", port=usable_port)
    with TCPServer(server_address, StreamRequestHandler, bind_and_activate=False) as tcpd:
        tcpd.request_queue_size = 1
        try:
            tcpd.server_bind()
            tcpd.server_activate()
        except Exception:
            tcpd.server_close()
            raise
        yield tcpd


class BusyHandler(StreamRequestHandler):
    def handle(self) -> None:
        time.sleep(2)


@pytest.fixture
def tcp_server(tcpd):
    sa = tcpd.socket.getsockname()
    t = threading.Thread(target=tcpd.serve_forever)
    t.start()
    yield sa[0], sa[1]
    tcpd.shutdown()


class TestTCPProbe:
    @pytest.fixture()
    def prober(self, tcpd):
        class SomeTCPProbe(TCPProbe):
            timeout = 1
            address = InternetAddress(*tcpd.socket.getsockname())

        return SomeTCPProbe()

    @pytest.fixture
    def dummy_prober(self, usable_port):
        class SomeTCPProbe(TCPProbe):
            timeout = 1
            address = InternetAddress(host="localhost", port=usable_port)

        return SomeTCPProbe()

    def test_success(self, prober, tcp_server):
        issues = prober.diagnose()
        assert len(issues) == 0

    def test_timeout(self, prober, tcpd):
        tcpd.RequestHandlerClass = BusyHandler
        prober.diagnose()
        prober.diagnose()
        issues = prober.diagnose()
        assert len(issues) == 1
        issue = issues[0]
        assert issue.fatal
        assert "Timeout, detail: timed out" in issue.description

    def test_no_server(self, dummy_prober):
        issues = dummy_prober.diagnose()
        assert len(issues) == 1
        issue = issues[0]
        assert issue.fatal
        assert "Connection refused" in issue.description
