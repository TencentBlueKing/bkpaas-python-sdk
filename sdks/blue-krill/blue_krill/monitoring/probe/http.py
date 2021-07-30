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
import logging
from typing import Dict, List

from blue_krill.monitoring.probe.base import Issue, VirtualProbe

try:
    import requests
except ImportError as _e:
    raise ImportError('Error loading http module: %s.\n' 'Did you install requests?' % _e) from _e


logger = logging.getLogger(__name__)


class HttpProbe(VirtualProbe):
    """
    A universal http probe, which send a GET request to url and only validate status code from response.

    Usage:
        class SomeHttpProbe(HttpProbe):
            name: str = "some"
            url: str = "http://localhost/ping"

        class SomeHttpsWithoutCa(HttpProbe):
            name: str = "some"
            url: str = "http://localhost/ping"
            verify: bool = False

        class SomeHttpWithAuth(HttpProbe):
            name: str = "some"
            url: str = "http://localhost/ping"
            params: Dict = {"token": "dummy"}
            headers: Dict = {"Authorization": "Basic YWxhZGRpbjpvcGVuc2VzYW1l"}

    """

    url: str
    headers: Dict = {}
    params: Dict = {}
    verify: bool = True
    timeout: int = 30
    desired_code: int = requests.codes.ok

    def diagnose(self) -> List[Issue]:
        try:
            response = requests.get(
                url=self.url, params=self.params, headers=self.headers, timeout=self.timeout, verify=self.verify
            )
        except requests.Timeout as e:
            logger.exception("Request %s timeout", self.url)
            return [Issue(fatal=True, description=f"Request {self.url} timeout, detail: {e}")]
        except requests.RequestException as e:
            logger.exception("An exception occurs when requesting %s", self.url)
            return [Issue(fatal=True, description=str(e))]
        return self.validate_response(response)

    def validate_response(self, response: requests.Response) -> List[Issue]:
        if response.status_code != self.desired_code:
            return [Issue(fatal=True, description=f"Undesired status code<{response.status_code}>")]
        return []


class BKHttpProbe(HttpProbe):
    """A specialized http probe for internal projects, which validate a formatted `healthz` response.

    Example Formatted Response:
        {result: bool, message: str}

    When bool('result') is False, report an issue with 'message'.
    """

    def validate_response(self, response: requests.Response) -> List[Issue]:
        if response.status_code != self.desired_code:
            return [Issue(fatal=True, description=f"Undesired status code<{response.status_code}>")]

        try:
            data = response.json()
        except Exception:  # pylint: disable=broad-except
            logger.exception("invalid data: %s", response.content)
            return [Issue(fatal=True, description=f"invalid data: {response.content!r}")]

        if not bool(data.get("result")):
            return [Issue(fatal=True, description=data.get("message", "missing message."))]
        return []
