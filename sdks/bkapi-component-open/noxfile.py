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

import nox

nox.needs_version = ">=2021.6.12"


@nox.session(python=["2.7", "3.6", "3.7", "3.8"])
def install(session):
    session.install(".")

    package_file = session.run(
        "python",
        "-c",
        "print(__import__('bkapi_component.open').open.__file__)",
        silent=True,
    ).strip()
    namespace_path = os.path.dirname(os.path.dirname(package_file))

    session.run("python", "-m", "pip", "uninstall", "-y", "bkapi-component-open")

    assert os.path.isdir(namespace_path)
