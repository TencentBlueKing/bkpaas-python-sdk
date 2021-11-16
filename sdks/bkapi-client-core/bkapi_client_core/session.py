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
from typing import Any, Dict, Optional

from requests import Session as RequestSession
from requests.hooks import dispatch_hook
from requests.models import RequestHooksMixin
from requests.sessions import merge_setting

from bkapi_client_core import __version__


class Session(RequestSession, RequestHooksMixin):
    """Session handle http requests, make a request and return the response

    BaseClient needs a context for sharing data, in different requests.
    It reuses requests.Session as this context and expands some data.
    Thus, BaseClient focuses on operations, and Session processes data.
    """

    default_user_agent = "bkapi-client/%s" % __version__

    def __init__(self, **kwargs):
        super(Session, self).__init__()
        self.path_params = {}  # type: Dict[str, Any]
        self.timeout = None  # type: Optional[float]
        self.set_user_agent(self.default_user_agent)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def handle(
        self,
        url,  # type: str
        path_params=None,  # type: Dict[str, Any]
        timeout=None,  # type: float
        **kwargs  # type: Any
    ):
        url = url.format(**merge_setting(path_params, self.path_params))
        return self.request(url=url, timeout=timeout or self.timeout, **kwargs)

    def set_user_agent(
        self,
        user_agent,  # type: str
    ):
        """
        Set User-Agent header

        :param user_agent: user agent identify string
        :type user_agent: str
        """
        self.headers["User-Agent"] = user_agent

    def dispatch_hook(
        self,
        event,  # str
        data,  # Any
        **extras  # type: Any
    ):
        dispatch_hook(event, self.hooks, data, **extras)

    def declare_hook(
        self,
        event,  # type:str
    ):
        self.hooks[event] = []
