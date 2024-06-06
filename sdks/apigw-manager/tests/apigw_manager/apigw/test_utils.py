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
import os
import tempfile
import zipfile

import pytest
from django.conf import settings
from packaging.version import InvalidVersion

from apigw_manager.apigw.utils import ZipArchiveFile, get_configuration, parse_value_list, parse_version


class TestGetConfiguration:
    def test_app_code(self, settings, faker):
        settings.BK_APP_CODE = faker.color()

        configuration = get_configuration()

        assert configuration.bk_app_code == settings.BK_APP_CODE

    def test_gateway_name(self, settings, faker):
        settings.BK_APIGW_NAME = faker.color()

        configuration = get_configuration()

        assert configuration.gateway_name == settings.BK_APIGW_NAME

    def test_app_secret(self, settings, faker):
        settings.BK_APP_SECRET = faker.color()

        configuration = get_configuration()

        assert configuration.bk_app_secret == settings.BK_APP_SECRET

    def test_jwt_provider_cls(self, settings, faker):
        settings.BK_APIGW_JWT_PROVIDER_CLS = faker.color()

        configuration = get_configuration()

        assert configuration.jwt_provider_cls == settings.BK_APIGW_JWT_PROVIDER_CLS

    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        [
            (
                    {},
                    "",
            ),
            (
                    {"host": "http://apigw.svc/api/test/prod/"},
                    "http://apigw.svc/api/test/prod",
            ),
            (
                    {"host": "http://apigw.svc/api/test/prod"},
                    "http://apigw.svc/api/test/prod",
            ),
        ],
    )
    def test_host_by_kwargs(self, settings, kwargs, expected):
        settings.BK_APIGATEWAY_API_STAGE_URL = ""
        settings.BK_API_URL_TMPL = ""

        configuration = get_configuration(**kwargs)

        assert configuration.host == expected

    @pytest.mark.parametrize(
        ("fake_settings", "expected"),
        [
            (
                    {},
                    "",
            ),
            (
                    {
                        "BK_APIGATEWAY_API_STAGE_URL": "http://apigw.svc/api/bk-apigateway/prod",
                    },
                    "http://apigw.svc/api/bk-apigateway/prod",
            ),
            (
                    {"BK_API_URL_TMPL": "http://apigw.svc/api/{api_name}/"},
                    "http://apigw.svc/api/bk-apigateway/prod",
            ),
            (
                    {
                        "BK_API_URL_TMPL": "http://apigw.svc/api/{api_name}",
                    },
                    "http://apigw.svc/api/bk-apigateway/prod",
            ),
        ],
    )
    def test_host_by_settings(self, settings, fake_settings, expected):
        settings.BK_APIGATEWAY_API_STAGE_URL = ""
        settings.BK_API_URL_TMPL = ""
        for key, value in fake_settings.items():
            setattr(settings, key, value)

        configuration = get_configuration()

        assert configuration.host == expected


class TestParseValueList:
    def test_multiple_values(self):
        result = parse_value_list(
            "int:1",
            'int_str:"2"',
            "str:str",
            "float:3.0",
        )

        assert result["int"] == 1
        assert result["int_str"] == "2"
        assert result["str"] == "str"
        assert result["float"] == 3.0


class TestZipArchiveFile:
    def test_archive(self):
        file_path = os.path.join(settings.BASE_DIR, "tests", "files", "docs")
        with tempfile.TemporaryFile() as temp_file:
            ZipArchiveFile.archive(file_path, temp_file)

            with zipfile.ZipFile(temp_file, "r") as zip_:
                assert zip_.namelist() == ["zh/get.md"]

    def test_get_archived_files(self):
        file_path = os.path.join(settings.BASE_DIR, os.path.join("tests", "files", "docs", "zh", "get.md"))
        result = ZipArchiveFile._get_archived_files(file_path)
        assert result == {file_path: "get.md"}

        file_path = os.path.join(settings.BASE_DIR, "tests", "files", "docs")
        result = ZipArchiveFile._get_archived_files(file_path)
        assert result == {os.path.join(file_path, "zh", "get.md"): os.path.join("zh", "get.md")}


class TestVersion:

    def test_valid_versions(self):
        valid_versions = [
            "1.0.0",
            "2.1.0-alpha",
            "3.0.0-beta.1",
            "4.0.0-rc.1",
            "5.0.0+build.1",
            "6.0.0-alpha+build.1",
            "7.0.0-feature-layered-alpha2",
            "8.0.0-feature-layered-alpha.2",
            "3.14.1-feature-layered-alpha2"
        ]
        for version in valid_versions:
            try:
                parse_version(version)
            except InvalidVersion:
                pytest.fail(f"Valid version '{version}' raised InvalidVersion")

