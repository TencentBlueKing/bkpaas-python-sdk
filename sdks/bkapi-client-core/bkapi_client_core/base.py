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

from requests import Response
from typing_extensions import Protocol


class ClientProtocol(Protocol):
    """ClientProtocol represents a protocol required to implement a client that handles HTTP requests"""

    def handle_request(
        self,
        operation,  # type: Operation
        context,  # type: Dict[str, Any]
    ):
        # type: (...) -> Optional[Response]
        raise NotImplementedError

    def parse_response(
        self,
        operation,  # type: Operation
        response,  # type: Optional[Response]
    ):
        # type: (...) -> Any
        raise NotImplementedError


class ManagerProtocol(Protocol):
    """ManagerProtocol is a protocol that the classes required to manage resources."""

    def get_client(self):
        # type: (...) -> ClientProtocol
        """Return a client for the Operation requesting"""
        raise NotImplementedError


class OperationResource(object):
    """OperationResource represents a single Operation or an OperationGroup"""

    def __init__(
        self,
        name="",  # type: str
        manager=None,  # type: ManagerProtocol
    ):
        self.name = name
        self._manager = manager

    def __str__(self):
        if not self._manager:
            return self.name

        return "%s.%s" % (self._manager, self.name)

    def _get_manager(self):
        if self._manager is None:
            raise ValueError("manager should not be None")

        return self._manager

    def _get_client(self):
        manager = self._get_manager()
        return manager.get_client()

    def bind(
        self,
        name,  # type: str
        manager,  # type: ManagerProtocol
    ):
        """
        Bind to Manger using a given name

        :param name: attribute name
        :type name: str
        :param manager: the manager of this resource
        :type manager: ManagerProtocol
        """
        if name:
            self.name = name
        self._manager = manager


class Operation(OperationResource):
    """
    Operation is the HTTP method used to manipulate the path,
    represents a packaged request operation.
    """

    def __init__(
        self,
        name="",  # type: str
        manager=None,  # type: ManagerProtocol
        method="",  # type: str
        path="",  # type: str
        bkapi_config=None,  # type: Dict[str, Any]
        **properties  # type: Dict[str, Any]
    ):
        self.method = method
        self.path = path
        self._bkapi_config = bkapi_config or {}
        self._properties = properties
        super(Operation, self).__init__(name, manager)

    def _get_context(self, **kwargs):
        # type: (...) -> Dict[str, Any]
        context = {
            "method": self.method,
            "path": self.path,
        }
        context.update(kwargs)

        return context

    def __call__(
        self,
        data=None,  # type: Optional[Any]
        path_params=None,  # type: Optional[Dict[str, Any]]
        params=None,  # type: Optional[Dict[str, Any]]
        headers=None,  # type: Optional[Dict[str, Any]]
        timeout=None,  # type: Optional[float]
        proxies=None,  # type: Optional[Dict[str, Any]]
        verify=None,  # type: Optional[bool]
        **kwargs
    ):
        """
        Request to the api and return the structured result which parsed by the client.

        :param data: Request data to sent.
        :param path_params: Variables parts of the url path.
        :param params: Variables in the query string.
        :param headers: HTTP Headers to send.
        :param timeout: Seconds to wait for the server to send data before giving up.
        :param proxies: Protocol proxies mappings.
        :param verify: Should we verify the server TLS certificate.
        """
        client = self._get_client()

        response = client.handle_request(
            self,
            self._get_context(
                data=data,
                path_params=path_params,
                params=params,
                headers=headers,
                timeout=timeout,
                proxies=proxies,
                verify=verify,
                **kwargs
            ),
        )

        return client.parse_response(self, response)

    def request(
        self,
        data=None,  # type: Optional[Any]
        path_params=None,  # type: Optional[Dict[str, Any]]
        params=None,  # type: Optional[Dict[str, Any]]
        headers=None,  # type: Optional[Dict[str, Any]]
        timeout=None,  # type: Optional[float]
        proxies=None,  # type: Optional[Dict[str, Any]]
        verify=None,  # type: Optional[bool]
        **kwargs
    ):
        # type: (...) -> Optional[Response]
        """
        Request to the api and return the Response directly.

        :param data: Request data to sent.
        :param path_params: Variables parts of the url path.
        :param params: Variables in the query string.
        :param headers: HTTP Headers to send.
        :param timeout: Seconds to wait for the server to send data before giving up.
        :param proxies: Protocol proxies mappings.
        :param verify: Should we verify the server TLS certificate.
        """
        client = self._get_client()

        return client.handle_request(
            self,
            self._get_context(
                data=data,
                path_params=path_params,
                params=params,
                headers=headers,
                timeout=timeout,
                proxies=proxies,
                verify=verify,
                **kwargs
            ),
        )


class OperationGroup(OperationResource):
    """
    OperationGroup provides grouping management capabilities for Operations,
    and also providing the dynamic registration mechanisms.
    """

    def get_client(self):
        """
        Returns the client acquired by the previous level.

        :return: client
        :rtype: ClientProtocol
        """
        return self._get_client()

    def register(
        self,
        name,  # type: str
        operation,  # type: Operation
    ):
        """
        Register the operation using the specified name.

        :param name: attribute name
        :type name: str
        :param operation: operation instance
        :type operation: Operation
        :raises ValueError: when the operation has already been registered or name is invalid.
        """

        if not name:
            raise ValueError("operation name should not be empty")

        if hasattr(self, name):
            raise ValueError("operation already registered")

        operation.bind(name, self)
        setattr(self, name, operation)

    def __getattr__(
        self,
        name,  # type: str
    ):
        # type: (...) -> Operation
        """
        This is a trick to provide intelligence completion for dynamic registered operations.

        :raises AttributeError:
        """
        raise AttributeError(name)
