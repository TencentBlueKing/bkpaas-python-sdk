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
from bkapi_client_core.exceptions import PathParamsMissing
from bkapi_client_core.session import Session


class TestSession:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.session = Session()

    def test_init(self):
        session = Session(headers={"X-Testing": "1"})
        assert session.headers["X-Testing"] == "1"

    @pytest.mark.parametrize(
        "url, path_params, session_path_params",
        [
            ("http://example.com/red/", {}, {}),
            ("http://example.com/{ color }/", {"color": "red"}, {}),
            ("http://example.com/{color}/", {"color": "red"}, {}),
            ("http://example.com/{color-name}/", {"color-name": "red"}, {}),
            ("http://example.com/{color_name}/", {"color_name": "red"}, {}),
            ("http://example.com/{color_name}/", {"color_name": "red"}, {"color_name": "green"}),
        ],
    )
    def test_handle(self, requests_mock, url, path_params, session_path_params):
        requests_mock.get("http://example.com/red/", json={"a": "b"})
        session = Session(**{"path_params": session_path_params})
        result = session.handle(url, method="GET", path_params=path_params)
        assert result.json() == {"a": "b"}

    def test_path_params_missing(self):
        session = Session()

        with pytest.raises(
            PathParamsMissing,
            match="url http://example.com/{color}/ path parameter is required: color",
        ):  # type: ignore
            session.handle("http://example.com/{color}/", method="GET")

    def test_user_agent(self, requests_mock, faker):
        url = faker.url()
        requests_mock.get(url)

        self.session.handle(url, method="GET")

        request = requests_mock.request_history[0]
        assert request.headers["User-Agent"] == self.session.default_user_agent

    def test_handle_error(self, requests_mock):
        requests_mock.get("http://example.com/echo/", exc=RuntimeError)
        with pytest.raises(RuntimeError):  # type: ignore
            self.session.handle("http://example.com/echo/", method="GET")

    def test_hook(self, mocker):
        hook = mocker.MagicMock()

        event = "test"
        session = Session()
        session.declare_hook(event)

        session.register_hook(event, hook)
        session.dispatch_hook(event, 1, has_extra=True)
        hook.assert_called_once_with(1, has_extra=True)

        session.deregister_hook(event, hook)
        session.dispatch_hook(event, 1, has_extra=True)
        hook.assert_called_once_with(1, has_extra=True)
