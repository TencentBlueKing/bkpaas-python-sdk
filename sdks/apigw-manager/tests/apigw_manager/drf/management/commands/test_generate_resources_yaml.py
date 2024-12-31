# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
# Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from unittest.mock import Mock

import pytest
from apigw_manager.drf.management.commands.generate_resources_yaml import (
    post_process_inject_method_and_path,
    post_process_only_keep_the_apis_with_specified_tags,
)


@pytest.fixture()
def django_settings_subpath_empty(settings):
    settings.BK_APIGW_STAGE_BACKEND_SUBPATH = ""


@pytest.fixture()
def django_settings_subpath(settings):
    settings.BK_APIGW_STAGE_BACKEND_SUBPATH = "/mock"


class TestPostProcess:
    def test_only_keep_the_apis_with_specified_tags(self):
        tags = ["open"]

        f = post_process_only_keep_the_apis_with_specified_tags(tags)

        # no paths
        result1 = {"hello": "world"}
        data1 = f(result1, Mock(), Mock(), Mock())

        assert data1 == result1

        # with paths, no tag hit
        result2 = {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["close"]}},
            }
        }
        data2 = f(result2, Mock(), Mock(), Mock())
        assert data2 == {"paths": {}}

        # with paths, tag hit
        result3 = {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["open"]}, "post": {"tags": ["close"]}},
                "/api/v1/yyy": {"get": {"tags": ["close"]}, "post": {"tags": ["close"]}},
            }
        }
        data3 = f(result3, Mock(), Mock(), Mock())
        assert data3 == {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["open"]}},
            }
        }

    def test_post_process_inject_method_and_path_no_subpath(self, django_settings_subpath_empty):
        f = post_process_inject_method_and_path

        # no paths
        result1 = {"hello": "world"}
        data1 = f(result1, Mock(), Mock(), Mock())

        assert data1 == result1

        # with paths
        result2 = {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["open"], "x-bk-apigateway-resource": {"backend": {}}}},
            }
        }
        data2 = f(result2, Mock(), Mock(), Mock())
        assert data2 == {
            "paths": {
                "/api/v1/xxx": {
                    "get": {
                        "tags": ["open"],
                        "x-bk-apigateway-resource": {"backend": {"method": "get", "path": "/api/v1/xxx"}},
                    }
                },
            }
        }

    def test_post_process_inject_method_and_path_with_subpath(self, django_settings_subpath):
        f = post_process_inject_method_and_path

        # no paths
        result1 = {"hello": "world"}
        data1 = f(result1, Mock(), Mock(), Mock())

        assert data1 == result1

        # with paths
        result2 = {
            "paths": {
                "/api/v1/xxx": {"get": {"tags": ["open"], "x-bk-apigateway-resource": {"backend": {}}}},
            }
        }
        data2 = f(result2, Mock(), Mock(), Mock())
        assert data2 == {
            "paths": {
                "/api/v1/xxx": {
                    "get": {
                        "tags": ["open"],
                        "x-bk-apigateway-resource": {"backend": {"method": "get", "path": "/mock/api/v1/xxx"}},
                    }
                },
            }
        }
