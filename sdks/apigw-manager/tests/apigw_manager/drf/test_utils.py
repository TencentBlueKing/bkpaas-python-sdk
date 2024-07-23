"""
* TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
"""

import os
import pytest
from unittest import mock


from apigw_manager.drf.utils import (
    gen_apigateway_resource_config,
    get_logging_config_dict,
    get_default_database_config_dict,
)


class TestGenApigatewayResourceConfig:
    def test_gen(self):
        data = gen_apigateway_resource_config(
            is_public=False,
            allow_apply_permission=False,
            user_verified_required=True,
            app_verified_required=True,
            resource_permission_required=True,
            description_en="this is a test",
            match_subpath=False,
        )
        assert data == {
            "x-bk-apigateway-resource": {
                "isPublic": False,
                "matchSubpath": False,
                "backend": {
                    "name": "default",
                    "method": "",
                    "path": "",
                    "matchSubpath": False,
                    "timeout": 0,
                },
                "pluginConfigs": [],
                "allowApplyPermission": False,
                "authConfig": {
                    "userVerifiedRequired": True,
                    "appVerifiedRequired": True,
                    "resourcePermissionRequired": True,
                },
                "descriptionEn": "this is a test",
            }
        }


class TestGetLoggingConfigDict:
    def test_get(self):
        data = get_logging_config_dict(
            log_level="DEBUG",
            is_local=True,
            log_dir="/tmp",
            app_code="test",
        )

        expected_format = (
            "%(levelname)s [%(asctime)s] %(pathname)s "
            "%(lineno)d %(funcName)s %(process)d %(thread)d "
            "\n \t %(message)s \n"
        )
        assert data["formatters"]["verbose"]["format"] == expected_format


class TestGetDefaultDatabaseConfigDict:
    @mock.patch.dict(
        os.environ,
        {
            "GCS_MYSQL_NAME": "a",
            "GCS_MYSQL_USER": "b",
            "GCS_MYSQL_PASSWORD": "c",
            "GCS_MYSQL_HOST": "d",
            "GCS_MYSQL_PORT": "e",
        },
    )
    def test_get(self):
        settings_module = {"DB_PREFIX": "GCS_MYSQL"}
        data = get_default_database_config_dict(settings_module)
        assert data == {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "a",
            "USER": "b",
            "PASSWORD": "c",
            "HOST": "d",
            "PORT": "e",
            "OPTIONS": {"isolation_level": "repeatable read"},
        }
