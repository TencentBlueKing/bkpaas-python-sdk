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
import string
from typing import Any, Dict, List, Optional

from requests import Request
from requests import Session as RequestSession
from requests.hooks import dispatch_hook
from requests.models import RequestHooksMixin
from requests.sessions import merge_setting

from bkapi_client_core import __version__
from bkapi_client_core.config import HookEvent
from bkapi_client_core.exceptions import PathParamsMissing


class _UrlRender(string.Formatter):
    """_UrlRender should format the url by path parameters."""

    def __init__(self, url, common_path_params=None):
        self.url = url
        self.common_path_params = common_path_params

    def render(self, path_params=None):
        """Render the url with path_params."""
        real_path_params = merge_setting(path_params, self.common_path_params)

        return self.format(self.url, **real_path_params)

    def get_field(self, field_name, args, kwargs):
        """Get the path parameter."""

        # Why should I override `get_field` but not `get_value`?
        # Because the `get_field` implementation allow to drill down the attributes by `.`.
        # This feature is unnecessary and unsafe.

        field_name = field_name.strip()

        if field_name not in kwargs:
            raise PathParamsMissing(
                "url {url} path parameter is required: {field_name}".format(
                    field_name=field_name,
                    url=self.url,
                ),
            )

        return kwargs[field_name], field_name


_SESSION_HOOKS = {}  # type: Dict[str, List[Any]]


def register_global_hook(event, hook):
    """Register a session hook for the given event."""

    if event not in _SESSION_HOOKS:
        _SESSION_HOOKS[event] = []

    _SESSION_HOOKS[event].append(hook)


def deregister_global_hook(event, hook):
    """Deregister a session hook for the given event."""
    try:
        _SESSION_HOOKS[event].remove(hook)
        return True
    except ValueError:
        return False


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
        path_params=None,  # type: Optional[Dict[str, Any]]
        timeout=None,  # type: Optional[float]
        **kwargs  # type: Any
    ):
        render = _UrlRender(url, self.path_params)
        rendered_url = render.render(path_params)
        return self.request(url=rendered_url, timeout=timeout or self.timeout, **kwargs)

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

    def set_accept_language(
        self,
        language,  # type: Optional[str]
    ):
        """
        Set Accept-Language header, if language is blank or None, will delete the header.

        :param language: language code
        :type language: str
        """
        if language:
            self.headers["Accept-Language"] = language
        else:
            self.headers.pop("Accept-Language", None)

    def prepare_request(
        self,
        request,  # type: Request
    ):
        request = self.dispatch_hook(HookEvent.REQUEST, request)
        prepared_request = super(Session, self).prepare_request(request)
        return prepared_request

    def dispatch_hook(
        self,
        event,  # str
        data,  # Any
        **extras  # type: Any
    ):
        data = dispatch_hook(event, _SESSION_HOOKS, data, **extras)
        return dispatch_hook(event, self.hooks, data, **extras)

    def register_hook(
        self,
        event,  # type:str
        hook,  # type: Any
    ):
        if event not in self.hooks:
            self.hooks[event] = []

        super(Session, self).register_hook(event, hook)
