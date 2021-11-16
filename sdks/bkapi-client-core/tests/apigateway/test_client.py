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

from bkapi_client_core.apigateway.client import APIGatewayClient


class TestAPIGatewayClient:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIGatewayClient()

    def test_init(self, faker):
        assert self.client._endpoint == "/{stage_name}"

        endpoint = faker.pystr()
        stage = faker.pystr()
        client = APIGatewayClient(endpoint=endpoint, stage=stage)

        assert client._stage == stage
        assert client._endpoint == endpoint + "/{stage_name}"

    @pytest.mark.parametrize(
        "endpoint, stage, expected",
        [
            (None, None, "/prod"),
            ("http://bkapi.example.com", None, "http://bkapi.example.com/prod"),
            ("http://bkapi.example.com", "", "http://bkapi.example.com/"),
            ("http://bkapi.example.com", "test", "http://bkapi.example.com/test"),
            ("http://bkapi.example.com/backend/", None, "http://bkapi.example.com/backend/prod"),
            ("http://bkapi.example.com/backend", "", "http://bkapi.example.com/backend/"),
            ("http://bkapi.example.com/backend", "test", "http://bkapi.example.com/backend/test"),
        ],
    )
    def test_get_endpoint(self, endpoint, stage, expected):
        client = APIGatewayClient(endpoint=endpoint, stage=stage)
        assert client._get_endpoint() == expected
