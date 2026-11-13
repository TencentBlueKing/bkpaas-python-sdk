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


from functools import partial

import pytest
import yaml
from django.urls import path
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apigw_manager.core.configuration import Configuration
from apigw_manager.core.sync import Synchronizer
from apigw_manager.drf.management.commands.generate_resources_yaml import Command
from apigw_manager.drf.utils import gen_apigateway_resource_config


@pytest.mark.parametrize(
    ("deprecated", "deprecated_note"),
    [(True, "请使用 get_users_v2"), (True, ""), (False, "")],
)
def test_generate_and_sync_deprecated_resource(settings, tmp_path, monkeypatch, mocker, deprecated, deprecated_note):
    settings.REST_FRAMEWORK = {"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema"}

    class UsersView(APIView):
        authentication_classes = []
        permission_classes = []

        @extend_schema(
            operation_id="get_users",
            deprecated=deprecated,
            extensions=gen_apigateway_resource_config(deprecated_note=deprecated_note),
            responses={200: OpenApiTypes.OBJECT},
        )
        def get(self, request):
            return Response({})

    settings.BASE_DIR = tmp_path
    settings.BK_APIGW_STAGE_BACKEND_SUBPATH = "/backend"
    settings.BK_APIGW_STAGE_ENABLE_MCP_SERVERS = False
    monkeypatch.setattr(spectacular_settings, "POSTPROCESSING_HOOKS", [])
    monkeypatch.setattr(
        spectacular_settings,
        "DEFAULT_GENERATOR_CLASS",
        partial(SchemaGenerator, patterns=[path("users/", UsersView.as_view())]),
    )

    Command().handle()
    content = yaml.safe_load((tmp_path / "resources.yaml").read_text())
    operation = content["paths"]["/users/"]["get"]
    assert operation.get("deprecated", False) is deprecated
    extension = operation["x-bk-apigateway-resource"]
    if deprecated_note:
        assert extension["deprecatedNote"] == deprecated_note
    else:
        assert "deprecatedNote" not in extension
    assert extension["backend"]["path"] == "/backend/users/"
    assert extension["backend"]["method"] == "get"

    synchronizer = Synchronizer(Configuration())
    synchronizer.client = mocker.MagicMock()
    endpoint = synchronizer.client.api.v2_sync_resources
    endpoint.path = "/api/v2/sync/gateways/{gateway_name}/resources/"
    endpoint.return_value = {"data": {"added": [], "updated": [], "deleted": []}}

    result = synchronizer.sync_resources_config(content=content, delete=False)
    assert result == endpoint.return_value["data"]
    request_data = endpoint.call_args.kwargs["data"]
    assert request_data["delete"] is False
    assert yaml.safe_load(request_data["content"]) == content
