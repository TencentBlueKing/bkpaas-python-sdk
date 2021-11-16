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
from bkapi_client_core import exceptions
from bkapi_client_core.client import ResponseHeadersRepresenter


class TestResponseError:
    def test_str(self, mocker, faker):
        err = exceptions.ResponseError("error", response=None)
        assert str(err) == "error"

        err = exceptions.ResponseError(
            "error",
            response=mocker.MagicMock(),
            response_headers_representer=ResponseHeadersRepresenter(
                {
                    "X-Bkapi-Error-Code": faker.pystr(),
                    "X-Bkapi-Error-Message": faker.pystr(),
                    "X-Bkapi-Request-Id": faker.uuid4(),
                }
            ),
        )
        assert str(err).startswith("error")
        assert "request_id:" in str(err)

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
