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

import importlib
import sys

from apigw_manager.drf.apps import DrfConfig


def test_ready_imports_scheme(monkeypatch):
    drf_module = importlib.import_module("apigw_manager.drf")
    monkeypatch.delitem(sys.modules, "apigw_manager.drf.scheme", raising=False)
    monkeypatch.delattr(drf_module, "scheme", raising=False)
    assert not hasattr(drf_module, "scheme")

    config = DrfConfig("apigw_manager.drf", drf_module)
    config.ready()

    assert hasattr(drf_module, "scheme")
    assert "apigw_manager.drf.scheme" in sys.modules
