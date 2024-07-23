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
from unittest.mock import Mock
from apigw_manager.drf.authentication import ApiGatewayJWTAuthentication


class TestApiGatewayJWTAuthentication:
    def test_authenticate_header(self):
        authentication = ApiGatewayJWTAuthentication()
        header = authentication.authenticate_header(Mock())

        assert header == "HTTP_X_BKAPI_JWT"

    def test_make_app(self):
        authentication = ApiGatewayJWTAuthentication()
        app = authentication.make_app(bk_app_code="my_app", verified=True)

        assert app.bk_app_code == "my_app"
        assert app.verified
