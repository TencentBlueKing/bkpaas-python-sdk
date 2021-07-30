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
import socket
from typing import List, NamedTuple

from blue_krill.monitoring.probe.base import Issue, VirtualProbe

logger = logging.getLogger(__name__)


class InternetAddress(NamedTuple):
    host: str
    port: int


class TCPProbe(VirtualProbe):
    """
    Usage:
        class SomeTCPProbe(TCPProbe):
            name: str = "some"
            address: InternetAddress = InternetAddress(host="localhost", port=8080)

    """

    timeout: int = 30
    address: InternetAddress

    def diagnose(self) -> List[Issue]:
        try:
            sock = socket.create_connection(address=self.address, timeout=self.timeout)  # type: ignore
            sock.close()
        except socket.timeout as e:
            logger.exception("Connect %s Timeout", self.address)
            return [Issue(fatal=True, description=f"Connect {self.address} Timeout, detail: {str(e)}")]
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unknown Exception when connecting to %s", self.address)
            return [Issue(fatal=True, description=f"Unknown Exception<{type(e).__name__}>, detail: {str(e)}")]
        return []
