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
import requests

from bkapi_client_core import exceptions
from bkapi_client_core.client import ResponseHeadersRepresenter


class TestResponseError:
    @pytest.mark.parametrize(
        "error, response, headers, expected",
        [
            (
                "error",
                {
                    "status_code": 400,
                },
                {
                    "X-Bkapi-Error-Code": "code",
                    "X-Bkapi-Error-Message": "error-message",
                    "X-Bkapi-Request-Id": "abcdef",
                },
                "error, status_code: 400, request_id: abcdef, error_code: code, error-message",
            ),
            (
                "error",
                None,
                None,
                "error",
            ),
            (
                "error",
                {
                    "status_code": 400,
                },
                {
                    "X-Bkapi-Request-Id": "abcdef",
                },
                "error, status_code: 400, request_id: abcdef",
            ),
        ]
    )
    def test_str(self, mocker, error, response, headers, expected):
        err = exceptions.ResponseError(
            error,
            response=response and mocker.MagicMock(**response),
            response_headers_representer=ResponseHeadersRepresenter(headers),
        )
        assert str(err) == expected

    def test_error_code(self, mocker):
        err = exceptions.ResponseError(
            "",
            response=mocker.MagicMock(),
            response_headers_representer=ResponseHeadersRepresenter({"X-Bkapi-Error-Code": "error"}),
        )
        assert err.error_code == "error"

    def test_error_message(self, mocker):
        err = exceptions.ResponseError(
            "",
            response=mocker.MagicMock(),
            response_headers_representer=ResponseHeadersRepresenter({"X-Bkapi-Error-Message": "error"}),
        )
        assert err.error_message == "error"

    def test_request_id(self, mocker):
        err = exceptions.ResponseError(
            "",
            response=mocker.MagicMock(),
            response_headers_representer=ResponseHeadersRepresenter({"X-Bkapi-Request-Id": "abcdef"}),
        )
        assert err.request_id == "abcdef"

    def test_curl_command(self, mocker, faker):
        mocker.patch(
            "bkapi_client_core.exceptions.CurlRequest.to_curl", return_value="curl -X GET http://example.com",
        )
        err = exceptions.ResponseError(
            faker.pystr(),
            response=mocker.MagicMock(),
            response_headers_representer=ResponseHeadersRepresenter({"X-Bkapi-Request-Id": "abcdef"}),
        )
        assert err.curl_command == "curl -X GET http://example.com"

    @pytest.mark.parametrize(
        "request_, expected",
        [
            (None, None),
            ({"method": "GET"}, "GET"),
        ]
    )
    def test_request_method(self, mocker, faker, request_, expected):
        err = exceptions.ResponseError(
            faker.pystr(),
            request=request_ and mocker.MagicMock(**request_),
            response_headers_representer=ResponseHeadersRepresenter({"X-Bkapi-Request-Id": "abcdef"}),
        )
        assert err.request_method == expected

    @pytest.mark.parametrize(
        "request_, expected",
        [
            (None, ""),
            ({"url": "http://example.com/test?foo=bar"}, "http://example.com/test"),
        ]
    )
    def test_request_url(self, mocker, faker, request_, expected):
        err = exceptions.ResponseError(
            faker.pystr(),
            request=request_ and mocker.MagicMock(**request_),
            response_headers_representer=ResponseHeadersRepresenter({"X-Bkapi-Request-Id": "abcdef"}),
        )
        assert err.request_url == expected

    @pytest.mark.parametrize(
        "response, expected",
        [
            (None, None),
            ({"status_code": 200}, 200),
        ]
    )
    def test_request_status_code(self, mocker, faker, response, expected):
        err = exceptions.ResponseError(
            faker.pystr(),
            response=response and mocker.MagicMock(**response),
            response_headers_representer=ResponseHeadersRepresenter({"X-Bkapi-Request-Id": "abcdef"}),
        )
        assert err.response_status_code == expected
