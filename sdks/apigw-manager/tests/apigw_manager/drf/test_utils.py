# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) Tencent. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import os
from unittest import mock

import pytest

from apigw_manager.drf.utils import (
    gen_apigateway_resource_config,
    get_default_database_config_dict,
    get_logging_config_dict,
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

    def test_gen_with_mcp_and_disabled_app_verification(self, settings):
        settings.BK_APIGW_STAGE_ENABLE_MCP_SERVERS = True

        data = gen_apigateway_resource_config(
            app_verified_required=False,
            resource_permission_required=True,
            plugin_configs=[{"name": "test-plugin"}],
            none_schema=True,
            enable_mcp=True,
        )

        assert data == {
            "x-bk-apigateway-resource": {
                "isPublic": True,
                "matchSubpath": False,
                "backend": {
                    "name": "default",
                    "method": "",
                    "path": "",
                    "matchSubpath": False,
                    "timeout": 0,
                },
                "pluginConfigs": [{"name": "test-plugin"}],
                "allowApplyPermission": True,
                "authConfig": {
                    "userVerifiedRequired": False,
                    "appVerifiedRequired": False,
                    "resourcePermissionRequired": False,
                },
                "descriptionEn": "",
                "noneSchema": True,
                "enableMcp": True,
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

    @mock.patch.dict(os.environ, {"BKPAAS_PROCESS_TYPE": "beat"}, clear=False)
    @mock.patch("apigw_manager.drf.utils.random.sample", return_value=list("ab12"))
    @mock.patch("apigw_manager.drf.utils.os.path.exists", return_value=False)
    @mock.patch("apigw_manager.drf.utils.os.makedirs")
    def test_get_non_local(self, mocked_makedirs, mocked_exists, mocked_sample):
        data = get_logging_config_dict(
            log_level="INFO",
            is_local=False,
            log_dir="/tmp/apigw-manager-logs",
            app_code="test",
        )

        assert data["formatters"]["verbose"]["()"] == "pythonjsonlogger.jsonlogger.JsonFormatter"
        assert data["handlers"]["root"]["filename"] == os.path.join("/tmp/apigw-manager-logs", "beat-ab12-django.log")
        mocked_exists.assert_called_once_with("/tmp/apigw-manager-logs")
        mocked_makedirs.assert_called_once_with("/tmp/apigw-manager-logs")
        mocked_sample.assert_called_once()


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

    @mock.patch.dict(
        os.environ,
        {
            "GCS_MYSQL_NAME": "a",
            "MYSQL_NAME": "b",
        },
        clear=True,
    )
    def test_get_with_multiple_databases_requires_prefix(self):
        with pytest.raises(EnvironmentError, match="no DB_PREFIX config"):
            get_default_database_config_dict({})

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_get_without_supported_environment_variables(self, capsys):
        data = get_default_database_config_dict({})

        assert data == {}
        assert "DB_PREFIX config is not 'GCS_MYSQL' or 'MYSQL_NAME'" in capsys.readouterr().err

    @mock.patch.dict(
        os.environ,
        {
            "MYSQL_NAME": "a",
            "MYSQL_USER": "b",
            "MYSQL_PASSWORD": "c",
            "MYSQL_HOST": "d",
            "MYSQL_PORT": "e",
        },
        clear=True,
    )
    def test_get_with_mysql_prefix(self):
        data = get_default_database_config_dict({})

        assert data == {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "a",
            "USER": "b",
            "PASSWORD": "c",
            "HOST": "d",
            "PORT": "e",
            "OPTIONS": {"isolation_level": "repeatable read"},
        }
