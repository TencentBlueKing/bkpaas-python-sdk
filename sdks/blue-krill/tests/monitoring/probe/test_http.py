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
from unittest import mock

import pytest
import requests
import requests_mock as requests_mock_mod

from blue_krill.monitoring.probe.http import BKHttpProbe, HttpProbe


class TestHttpProbe:
    @pytest.fixture()
    def prober(self):
        class MockHttpProbe(HttpProbe):
            name = "mock"
            url = "mock://"
            desired_code = requests.codes.ok

        return MockHttpProbe()

    @mock.patch("blue_krill.monitoring.probe.http.requests.get", side_effect=requests.Timeout("timeout!"))
    def test_timeout(self, m_get, prober):
        issues = prober.diagnose()
        assert len(issues) == 1
        issue = issues[0]
        assert issue.fatal
        assert issue.description == "Request mock:// timeout, detail: timeout!"

    @pytest.mark.parametrize("status_code", [requests.codes.ok, requests.codes.bad, requests.codes.server_error])
    def test_desired_code(self, prober, requests_mock, status_code):
        requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, status_code=status_code)
        issues = prober.diagnose()
        if status_code == requests.codes.ok:
            assert len(issues) == 0
        else:
            assert len(issues) == 1
            issue = issues[0]
            assert issue.fatal
            assert issue.description == f"Undesired status code<{status_code}>"


class TestBKHttpProbe:
    @pytest.fixture()
    def prober(self):
        class MockHttpProbe(BKHttpProbe):
            name = "mock"
            url = "mock://"
            desired_code = requests.codes.ok

        return MockHttpProbe()

    @pytest.mark.parametrize(
        "resp_text, expected",
        [
            ("--", "invalid data: b'--'"),
            ("{}", "missing message."),
            ('{"result": false}', "missing message."),
            ('{"result": false, "message": "Oops!!"}', "Oops!!"),
        ],
    )
    def test_validate_response(self, prober, requests_mock, resp_text, expected):
        requests_mock.register_uri(requests_mock_mod.ANY, requests_mock_mod.ANY, text=resp_text)
        issues = prober.diagnose()
        assert len(issues) == 1
        issue = issues[0]
        assert issue.fatal
        assert issue.description == expected
