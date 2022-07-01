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
from prometheus_client import CollectorRegistry
from requests.exceptions import RequestException

from bkapi_client_core.config import HookEvent
from bkapi_client_core.prometheus import Collector, enable_collector


@pytest.fixture(autouse=True)
def mock_register_global_hook(mocker):
    return mocker.patch("bkapi_client_core.session.register_global_hook")


@pytest.fixture()
def mock_registry():
    return CollectorRegistry()


@pytest.fixture()
def mock_operation(mocker):
    operation = mocker.MagicMock()
    return operation


def test_enable_collector(mocker, mock_registry, mock_register_global_hook):
    enable_collector(registry=mock_registry)
    enable_collector(registry=mock_registry)  # this is not work

    assert mock_register_global_hook.call_count == 2
    mock_register_global_hook.assert_any_call(HookEvent.OPERATION_PREPARED, mocker.ANY)
    mock_register_global_hook.assert_any_call(HookEvent.OPERATION_ERROR, mocker.ANY)


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
        "request_size, request_headers, response_size, response_headers",
        [
            [0, {}, 0, {}],
            [0, {"Content-Length": ""}, 0, {"Content-Length": ""}],
            [123, {"Content-Length": "123"}, 456, {"Content-Length": "456"}],
            [0, {"Content-Length": "NAN"}, 0, {"Content-Length": "NAN"}],
        ],
    )
    def test_response_hook(
        self,
        faker,
        mocker,
        requests_mock,
        mock_operation,
        mock_registry,
        request_size,
        request_headers,
        response_size,
        response_headers,
    ):
        url = faker.url()
        requests_mock.get(url, json={"result": True})
        response = requests.get(url)
        response.request.headers = request_headers
        response.headers = response_headers

        self.collector.response_hook(response, mock_operation)

        assert (
            mock_registry.get_sample_value(
                "bkapi_requests_duration_seconds_count",
                {
                    "operation": str(mock_operation),
                    "method": str(mock_operation.method),
                },
            )
            == 1
        )
        assert (
            mock_registry.get_sample_value(
                "bkapi_responses_total",
                {
                    "operation": str(mock_operation),
                    "method": str(mock_operation.method),
                    "status": "200",
                },
            )
            == 1
        )

        if request_size:
            assert (
                mock_registry.get_sample_value(
                    "bkapi_requests_body_bytes_sum",
                    {
                        "operation": str(mock_operation),
                        "method": str(mock_operation.method),
                    },
                )
                == request_size
            )

        if response_size:
            assert (
                mock_registry.get_sample_value(
                    "bkapi_responses_body_bytes_sum",
                    {
                        "operation": str(mock_operation),
                        "method": str(mock_operation.method),
                    },
                )
                == response_size
            )

    def test_error_hook(self, mocker, mock_operation, mock_registry):
        error = RequestException("test")

        self.collector.error_hook(error, mock_operation)

        assert (
            mock_registry.get_sample_value(
                "bkapi_failures_total",
                {
                    "operation": str(mock_operation),
                    "method": str(mock_operation.method),
                    "error": "RequestException",
                },
            )
            == 1.0
        )
