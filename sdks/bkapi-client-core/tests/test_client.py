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
import pytest
from requests.exceptions import RequestException

from bkapi_client_core.base import Operation, OperationGroup
from bkapi_client_core.client import BaseClient, RequestContextBuilder, ResponseHeadersRepresenter
from bkapi_client_core.config import HookEvent
from bkapi_client_core.exceptions import APIGatewayResponseError, EndpointNotSetError, ResponseError
from bkapi_client_core.property import bind_property
from bkapi_client_core.session import Session


class TestRequestContextBuilder:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.builder = RequestContextBuilder()

    @pytest.mark.parametrize(
        "endpoint,path,excepted",
        [
            ("http://example.com", "api/test", "http://example.com/api/test"),
            ("http://example.com", "/api/test", "http://example.com/api/test"),
            ("http://example.com", "api/test/", "http://example.com/api/test/"),
            ("http://example.com", "/api/test/", "http://example.com/api/test/"),
            ("http://example.com/api", "/test/", "http://example.com/api/test/"),
        ],
    )
    def test_build_url(self, endpoint, path, excepted):
        context = {}
        self.builder.build_url(context, endpoint, path)
        assert context["url"] == excepted

    @pytest.mark.parametrize(
        "method,params,data,excepted_params,excepted_json",
        [
            (
                "GET",
                None,
                {"x": 1},
                {"x": 1},
                None,
            ),
            (
                "GET",
                {},
                {"x": 1},
                {"x": 1},
                None,
            ),
            (
                "GET",
                {"y": 2},
                {"x": 1},
                {"x": 1, "y": 2},
                None,
            ),
            (
                "GET",
                {"x": 2},
                {"x": 1, "y": 2},
                {"x": 2, "y": 2},
                None,
            ),
            (
                "HEAD",
                {},
                {"x": 1},
                {"x": 1},
                None,
            ),
            (
                "HEAD",
                {"y": 2},
                {"x": 1},
                {"x": 1, "y": 2},
                None,
            ),
            (
                "OPTIONS",
                {"y": 2},
                {"x": 1},
                {"x": 1, "y": 2},
                None,
            ),
            (
                "POST",
                None,
                {"x": 1},
                None,
                {"x": 1},
            ),
            (
                "POST",
                {},
                {"x": 1},
                {},
                {"x": 1},
            ),
            (
                "POST",
                {"y": 2},
                {"x": 1},
                {"y": 2},
                {"x": 1},
            ),
            (
                "POST",
                None,
                None,
                None,
                None,
            ),
            (
                "GET",
                None,
                None,
                None,
                None,
            ),
            (
                "DELETE",
                {},
                {"x": 1},
                {},
                {"x": 1},
            ),
            (
                "DELETE",
                {"y": 2},
                {"x": 1},
                {"y": 2},
                {"x": 1},
            ),
        ],
    )
    def test_build_data(self, method, params, data, excepted_params, excepted_json):
        context = {"params": params, "method": method}
        self.builder.build_data(context, data)

        assert context.get("params") == excepted_params
        assert context.get("json") == excepted_json

    @pytest.mark.parametrize(
        "input,output",
        [
            (
                {"endpoint": "http://example.com", "path": "/api/", "method": "GET"},
                {"url": "http://example.com/api/", "method": "GET"},
            ),
            (
                {
                    "endpoint": "http://example.com",
                    "path": "/api/",
                    "method": "POST",
                    "params": {"x": 1},
                    "timeout": 1.0,
                },
                {
                    "url": "http://example.com/api/",
                    "method": "POST",
                    "params": {"x": 1},
                    "timeout": 1.0,
                },
            ),
        ],
    )
    def test_build_request_context(self, input, output):
        assert self.builder.build_request_context(**input) == output


class TestResponseHeadersRepresenter:
    @pytest.mark.parametrize(
        "headers, key, default, expected",
        [
            (None, "test", "", ""),
            ({"x-color": "red"}, "x-color", "", "red"),
            ({"x-color": "red"}, "x-color-name", "", ""),
        ],
    )
    def test_get_header(self, headers, key, default, expected):
        headers = ResponseHeadersRepresenter(headers)
        assert headers._get_header(key, default) == expected

    def test_error_code(self):
        headers = ResponseHeadersRepresenter({"X-Bkapi-Error-Code": "error"})
        assert headers.error_code == "error"

    def test_error_message(self):
        headers = ResponseHeadersRepresenter({"X-Bkapi-Error-Message": "error"})
        assert headers.error_message == "error"

    def test_request_id(self, mocker):
        headers = ResponseHeadersRepresenter({"X-Bkapi-Request-Id": "abcdef"})
        assert headers.request_id == "abcdef"

    @pytest.mark.parametrize(
        "headers, expected",
        [
            ({"X-Bkapi-Error-Code": "error"}, True),
            ({}, False),
        ],
    )
    def test_has_apigateway_error(self, headers, expected):
        headers = ResponseHeadersRepresenter(headers)
        assert headers.has_apigateway_error == expected

    @pytest.mark.parametrize(
        "headers, expected",
        [
            (
                {
                    "X-Bkapi-Request-Id": "abcdef",
                    "X-Bkapi-Error-Code": "foo",
                    "X-Bkapi-Error-Message": "error",
                },
                "request_id: abcdef, error_code: foo, error",
            ),
            (
                {
                    "X-Bkapi-Request-Id": "abcdef",
                    "X-Bkapi-Error-Code": "foo",
                },
                "request_id: abcdef, error_code: foo",
            ),
            (
                {
                    "X-Bkapi-Request-Id": "abcdef",
                },
                "request_id: abcdef",
            ),
        ],
    )
    def test_str(self, headers, expected):
        representer = ResponseHeadersRepresenter(headers)
        assert str(representer) == expected


class TestBaseClient:
    @pytest.fixture(autouse=True)
    def setup(self, faker, requests_mock):
        self.client = BaseClient(faker.url())

    def test_client_default_name(self):
        client = BaseClient()
        assert client.name == BaseClient.name

    def test_client_name(self, faker):
        name = faker.color_name()
        client = BaseClient(name=name)
        assert client.name == name

    def test_reuse_session_connection(self, mocker, faker, requests_mock):
        url = faker.url()
        requests_mock.get(url, json={"result": True})

        client = BaseClient(url)
        mock_close = mocker.patch.object(client, "close", return_value=None)

        # handle_request without `with`, will close
        client.handle_request(url, {"method": "GET"})
        mock_close.assert_called_once_with()

        mock_close.reset_mock()
        # handle_request in `with`, will not close
        with client:
            assert client._reuse_session_connection is True

            client.handle_request(url, {"method": "GET"})
            mock_close.assert_not_called()

            client.handle_request(url, {"method": "GET"})
            mock_close.assert_not_called()

        assert client._reuse_session_connection is False
        mock_close.assert_called_once_with()

    @pytest.mark.parametrize(
        "endpoint,operation_path,excepted_url",
        [
            ("http://example.com", "echo", "http://example.com/echo"),
            ("http://example.com/", "/echo", "http://example.com/echo"),
            ("http://example.com/api", "echo", "http://example.com/api/echo"),
            ("http://example.com/api/", "/echo", "http://example.com/api/echo"),
            ("http://example.com/v2", "action/echo", "http://example.com/v2/action/echo"),
        ],
    )
    def test_operation(
        self,
        requests_mock,
        faker,
        endpoint,
        operation_path,
        excepted_url,
    ):
        class Group(OperationGroup):
            echo = bind_property(Operation, method="GET", path=operation_path, name="echo")

        class Client(BaseClient):
            api = bind_property(Group, name="api")

        result = {"faker": faker.pystr()}
        requests_mock.get(excepted_url, json=result)
        client = Client(endpoint)

        assert client.api.echo() == result
        assert str(client.api.echo) == "client.api.echo"

    def test_handle(self, mocker, faker):
        session = Session()
        mock_handle = mocker.patch.object(session, "handle")

        endpoint = "http://example.com"
        client = BaseClient(endpoint=endpoint, session=session)
        operation = mocker.MagicMock()
        context = {"path": "test"}

        response = mock_handle.return_value

        assert client.handle_request(operation, context) is response
        session.handle.assert_called_once_with(url="http://example.com/test")

    def test_handle_request_hook(self, mocker, faker):
        def hook(context, operation):
            context["path"] = operation.name
            return context

        session = Session()
        mocker.patch.object(session, "handle")
        session.register_hook(HookEvent.OPERATION_PREPARED, hook)

        endpoint = "http://example.com"
        client = BaseClient(endpoint=endpoint, session=session)
        operation = mocker.MagicMock()
        operation.name = "hooked"
        context = {"path": "test"}

        client.handle_request(operation, context)
        session.handle.assert_called_once_with(url="http://example.com/hooked")

    def test_handle_error(self, mocker, faker):
        session = mocker.MagicMock()
        client = BaseClient(session=session, endpoint=faker.url())
        operation = mocker.MagicMock()
        context = mocker.MagicMock()

        session.handle.side_effect = RequestException

        with pytest.raises(RequestException):  # type: ignore
            client.handle_request(operation, context)

    def test_endpoint_not_set(self, mocker):
        session = mocker.MagicMock()
        client = BaseClient(session=session)
        operation = mocker.MagicMock()
        context = mocker.MagicMock()

        with pytest.raises(EndpointNotSetError):  # type: ignore
            client.handle_request(operation, context)

    def test_parse_response_error(self, mocker):
        mocker.patch.object(self.client, "_handle_response_content", side_effect=RequestException)

        with pytest.raises(RequestException):  # type: ignore
            self.client.parse_response(mocker.MagicMock(), mocker.MagicMock())

    @pytest.mark.parametrize(
        "response, expected_error",
        [
            (
                None,
                None,
            ),
            (
                {
                    "headers": {},
                },
                None,
            ),
            (
                {
                    "headers": {"X-Bkapi-Error-Code": "error"},
                },
                APIGatewayResponseError,
            ),
        ],
    )
    def test_check_response_apigateway_error(self, mocker, response, expected_error):
        if not expected_error:
            self.client.check_response_apigateway_error(response and mocker.MagicMock(**response))
            return

        with pytest.raises(expected_error):
            self.client.check_response_apigateway_error(mocker.MagicMock(**response))

    @pytest.mark.parametrize(
        "session_headers, headers, expected",
        [
            (
                {"x-token": "test"},
                {"x-color": "red"},
                {"x-token": "test", "x-color": "red"},
            ),
            (
                {"x-token": "test"},
                {"X-Token": "red"},
                {"X-Token": "red"},
            ),
            (
                {"x-token": "test"},
                {"X_Token": "red"},
                {"x-token": "test", "X_Token": "red"},
            ),
        ],
    )
    def test_update_headers(self, mocker, faker, session_headers, headers, expected):
        client = BaseClient(endpoint=faker.url())
        client.session.headers = session_headers

        client.update_headers(headers)
        assert client.session.headers == expected

    @pytest.mark.parametrize(
        "auth,update_auth,expected",
        [
            (
                {},
                {"bk_app_code": "test-app", "bk_app_secret": "test-secret"},
                {"bk_app_code": "test-app", "bk_app_secret": "test-secret"},
            ),
            (
                {"bk_app_code": "test-app", "bk_app_secret": "test-secret"},
                {"bk_app_code": "test-app2", "bk_app_secret": "test-secret2"},
                {"bk_app_code": "test-app2", "bk_app_secret": "test-secret2"},
            ),
            (
                {"bk_app_code": "test-app"},
                {"bk_app_code": "test-app2", "bk_app_secret": "test-secret2"},
                {"bk_app_code": "test-app2", "bk_app_secret": "test-secret2"},
            ),
        ],
    )
    def test_update_bkapi_authorization(self, auth, update_auth, expected):
        client = BaseClient()
        client.update_bkapi_authorization(**update_auth)
        assert client.session.auth.auth == expected

    def test_update_bkapi_authorization_error(self, mocker):
        self.client.session.auth = mocker.MagicMock()
        with pytest.raises(TypeError):  # type: ignore
            self.client.update_bkapi_authorization(x="1")

    def test_set_timeout(self):
        self.client.set_timeout(1.0)
        assert self.client.session.timeout == 1.0

    def test_disable_ssl_verify(self):
        self.client.disable_ssl_verify()
        assert self.client.session.verify is False

    def test_handler_exception(self, mocker):
        with pytest.raises(RequestException):  # type: ignore
            self.client._handle_exception(
                mocker.MagicMock(),
                mocker.MagicMock(),
                RequestException(response=None),
            )

    def test_handle_response_content(self, mocker):
        assert self.client._handle_response_content(mocker.MagicMock(), None) is None

        response = {
            "headers": {"X-Bkapi-Request-Id": "abcd"},
            "json.return_value": {"foo": "bar"},
            "raise_for_status.return_value": None,
        }
        result = self.client._handle_response_content(None, mocker.MagicMock(**response))
        assert result == {"foo": "bar"}

    @pytest.mark.parametrize(
        "response",
        [
            {"headers": {"X-Bkapi-Error-Code": "error"}},
            {"raise_for_status.side_effect": RequestException("error")},
            {"json.side_effect": TypeError},
        ],
    )
    def test_handle_response_content_error(self, mocker, response):
        with pytest.raises(ResponseError):  # type: ignore
            self.client._handle_response_content(
                mocker.MagicMock(),
                response and mocker.MagicMock(**response),
            )
