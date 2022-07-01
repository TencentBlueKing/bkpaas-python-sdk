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

import time
from functools import partial
from typing import Any, Dict, List, Optional

from prometheus_client import REGISTRY, CollectorRegistry, Counter, Histogram
from requests import Response

from bkapi_client_core.base import Operation
from bkapi_client_core.config import HookEvent
from bkapi_client_core.session import register_global_hook

default_bytes_buckets = [
    0,
    1,
    2,
    4,
    8,
    16,
    32,
    64,
    128,
    256,
    512,
    1024,
    2048,
    4096,
    8192,
    16384,
    32768,
    65536,
    131072,
    262144,
    524288,
    1048576,
    2097152,
    4194304,
    8388608,
    16777216,
    33554432,
    67108864,
    134217728,
    268435456,
    536870912,
    float("inf"),
]
default_duration_buckets = [
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    7.5,
    10.0,
    25.0,
    50.0,
    75.0,
    float("inf"),
]


class Collector:
    def __init__(
        self,
        registry,  # type: CollectorRegistry
        namespace,  # type: str
        subsystem,  # type: str
        duration_buckets,  # type: List[float]
        bytes_buckets,  # type: List[float]
    ):

        self.metric_requests_duration_seconds = Histogram(
            "bkapi_requests_duration_seconds",
            "Histogram of requests duration by operation, method",
            ["operation", "method"],
            namespace=namespace,
            subsystem=subsystem,
            registry=registry,
            buckets=duration_buckets,
        )

        self.metric_requests_body_bytes = Histogram(
            "bkapi_requests_body_bytes",
            "Histogram of requests body bytes by operation, method",
            ["operation", "method"],
            namespace=namespace,
            subsystem=subsystem,
            registry=registry,
            buckets=bytes_buckets,
        )

        self.metric_responses_body_bytes = Histogram(
            "bkapi_responses_body_bytes",
            "Histogram of responses body bytes by operation, method",
            ["operation", "method"],
            namespace=namespace,
            subsystem=subsystem,
            registry=registry,
            buckets=bytes_buckets,
        )

        self.metric_responses_total = Counter(
            "bkapi_responses_total",
            "Count of responses by operation, method, status",
            ["operation", "method", "status"],
            namespace=namespace,
            subsystem=subsystem,
            registry=registry,
        )

    def _register_response_hook(
        self,
        response,  # type: Response
        bkapi_operation,  # type: Operation
        bkapi_request_at,  # type: float
        **kwargs  # type: Any
    ):
        end_at = time.time()
        name = str(bkapi_operation)
        method = bkapi_operation.method

        self.metric_requests_duration_seconds.labels(
            operation=name,
            method=method,
        ).observe(end_at - bkapi_request_at)

        self.metric_responses_total.labels(
            operation=name,
            method=method,
            status=response.status_code,
        ).inc()

        request_content_length = response.request.headers.get("Content-Length")
        if request_content_length and request_content_length.isdigit():
            self.metric_requests_body_bytes.labels(
                operation=name,
                method=method,
            ).observe(int(request_content_length))

        # this method should finish as fast as possible,
        # so it's not a good idea to read the response body to calculate the size
        response_content_length = response.headers.get("Content-Length")
        if response_content_length and response_content_length.isdigit():
            self.metric_responses_body_bytes.labels(
                operation=name,
                method=method,
            ).observe(int(response_content_length))

    def _register_request_hook(
        self,
        context,  # type: Dict[str, Any]
        operation,  # type: Operation
    ):
        hooks = context.setdefault("hooks", {})
        response_hooks = hooks.setdefault(HookEvent.RESPONSE, [])
        response_hooks.append(
            partial(
                self._register_response_hook,
                bkapi_operation=operation,
                bkapi_request_at=time.time(),
            )
        )

        return context

    def register_hook(self):
        register_global_hook(HookEvent.HANDLE_REQUEST_CONTEXT, self._register_request_hook)


_GLOBAL_COLLECTOR = None  # type: Optional[Collector]


def enable_collector(
    registry=REGISTRY,
    namespace="",
    subsystem="",
    duration_buckets=default_duration_buckets,
    bytes_buckets=default_bytes_buckets,
):
    """
    Enable bkapi prometheus collector
    """
    global _GLOBAL_COLLECTOR

    if _GLOBAL_COLLECTOR:
        return False

    _GLOBAL_COLLECTOR = Collector(
        registry=registry,
        namespace=namespace,
        subsystem=subsystem,
        duration_buckets=duration_buckets,
        bytes_buckets=bytes_buckets,
    )
    _GLOBAL_COLLECTOR.register_hook()
