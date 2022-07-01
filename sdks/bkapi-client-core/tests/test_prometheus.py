"""
 TencentBlueKing is pleased to support the open source community by
 making bkapi-client-core available.
 Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
 Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 You may obtain a copy of the License at http://opensource.org/licenses/MIT
 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 specific language governing permissions and limitations under the License.
"""


import pytest
import requests

from bkapi_client_core.config import HookEvent
from bkapi_client_core.prometheus import Collector, enable_collector


@pytest.fixture(autouse=True)
def mock_register_global_hook(mocker):
    return mocker.patch("bkapi_client_core.session.register_global_hook")


@pytest.fixture()
def mock_registry(mocker):
    return mocker.MagicMock()


def test_enable_collector(mocker, mock_registry, mock_register_global_hook):
    enable_collector(registry=mock_registry)
    enable_collector(registry=mock_registry)  # this is not work

    mock_register_global_hook.assert_called_once_with(HookEvent.HANDLE_REQUEST_CONTEXT, mocker.ANY)


class TestCollector:
    @pytest.fixture(autouse=True)
    def setup(self, mock_registry):
        self.collector = Collector(
            registry=mock_registry,
            namespace="",
            subsystem="",
            duration_buckets=[0, float("+inf")],
            bytes_buckets=[0, float("+inf")],
        )

    def test_request_hook(self, mocker):
        context = {}
        operation = mocker.MagicMock()

        result = self.collector.request_hook(context, operation)
        assert len(result["hooks"][HookEvent.RESPONSE]) == 1

    def test_request_hook_with_exists_hook(self, mocker):
        context = {
            "hooks": {
                HookEvent.RESPONSE: [mocker.MagicMock()],
            },
        }
        operation = mocker.MagicMock()

        result = self.collector.request_hook(context, operation)
        assert len(result["hooks"][HookEvent.RESPONSE]) == 2

    @pytest.mark.parametrize(
        "request_headers, response_headers",
        [
            [{}, {}],
            [{"Content-Length": ""}, {"Content-Length": ""}],
            [{"Content-Length": "178"}, {"Content-Length": "178"}],
            [{"Content-Length": "NAN"}, {"Content-Length": "NAN"}],
        ],
    )
    def test_response_hook(self, faker, mocker, requests_mock, request_headers, response_headers):
        url = faker.url()
        requests_mock.get(url, json={"result": True})
        response = requests.get(url)
        response.request.headers = request_headers
        response.headers = response_headers

        operation = mocker.MagicMock()
        self.collector

        self.collector.response_hook(response, operation)
