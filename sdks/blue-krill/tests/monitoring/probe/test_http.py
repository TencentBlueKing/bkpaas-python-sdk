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
from wsgiref.simple_server import make_server
from wsgiref.util import setup_testing_defaults

import pytest
from blue_krill.monitoring.probe.http import BKHttpProbe, HttpProbe
from requests import codes


class FakeApp:
    def __init__(self):
        self._init_status = '200 OK'
        self._init_headers = [('Content-type', 'text/plain; charset=utf-8')]
        self._init_handler = lambda: [b'ok']

        self.status = self._init_status
        self.headers = self._init_headers
        self.handler = self._init_handler

    def __call__(self, environ, start_response):
        setup_testing_defaults(environ)
        start_response(self.status, self.headers)
        return self.handler()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.status = self._init_status
        self.headers = self._init_headers
        self.handler = self._init_handler

    @staticmethod
    def timeout():
        time.sleep(2)
        return [b'timeout']


@pytest.fixture
def usable_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


@pytest.fixture
def fake_app():
    return FakeApp()


@pytest.fixture
def httpd(fake_app, usable_port):
    server_address = "localhost", usable_port
    with make_server(*server_address, fake_app) as httpd:
        yield httpd


@pytest.fixture
def http_server(httpd):
    sa = httpd.socket.getsockname()
    t = threading.Thread(target=httpd.serve_forever)
    t.start()
    yield sa[0], sa[1]
    httpd.shutdown()


class TestHttpProbe:
    @pytest.fixture()
    def prober(self, http_server):
        class MockHttpProbe(HttpProbe):
            name = "mock"
            url = f"http://{http_server[0]}:{http_server[1]}"
            desired_code = codes.ok
            timeout = 1

        return MockHttpProbe()

    def test_timeout(self, fake_app, prober):
        with fake_app as context:
            context.handler = fake_app.timeout
            issues = prober.diagnose()

        assert len(issues) == 1
        issue = issues[0]
        assert issue.fatal
        assert "Read timed out" in issue.description

    @pytest.mark.parametrize(
        "status, expected",
        [
            ("200 OK", codes.ok),
            ("400 BAD", codes.bad),
            ("500 SERVER_ERROR", codes.server_error),
        ],
    )
    def test_desired_code(self, prober, fake_app, status, expected):
        with fake_app as context:
            context.status = status
            issues = prober.diagnose()

        if expected == codes.ok:
            assert len(issues) == 0
        else:
            assert len(issues) == 1
            issue = issues[0]
            assert issue.fatal
            assert issue.description == f"Undesired status code<{expected}>"


class TestBKHttpProbe:
    @pytest.fixture
    def prober(self, http_server):
        class MockHttpProbe(BKHttpProbe):
            name = "mock"
            url = f"http://{http_server[0]}:{http_server[1]}"
            desired_code = codes.ok
            timeout = 1

        return MockHttpProbe()

    @pytest.mark.parametrize(
        "resp_text, expected",
        [
            (b"--", "invalid data: b'--'"),
            (b"{}", "missing message."),
            (b'{"result": false}', "missing message."),
            (b'{"result": false, "message": "Oops!!"}', "Oops!!"),
        ],
    )
    def test_validate_response(self, prober, fake_app, resp_text, expected):
        with fake_app as context:
            context.handler = lambda: [resp_text]
            issues = prober.diagnose()
        assert len(issues) == 1
        issue = issues[0]
        assert issue.fatal
        assert issue.description == expected
