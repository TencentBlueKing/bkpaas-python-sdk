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

from typing import Optional  # noqa

from bkapi_client_core.client import BaseClient
from bkapi_client_core.session import Session  # noqa


class ESBClient(BaseClient):
    name = "esb"

    def __init__(
        self,
        endpoint="",  # type: str
        session=None,  # type: Optional[Session]
        bk_api_ver="",  # type: str
        use_test_env=False,  # type: bool
        language=None,  # type: Optional[str]
    ):
        super(ESBClient, self).__init__(endpoint, session)

        self.set_bk_api_ver(bk_api_ver)
        self.set_use_test_env(use_test_env)
        self.set_language(language)

    def set_use_test_env(
        self,
        use_test_env,  # type: bool
    ):
        key = "X-Use-Test-Env"

        if use_test_env:
            self._set_header(key, "true")
        else:
            self._delete_header(key)

    def set_language(
        self,
        language,  # type: Optional[str]
    ):
        self.session.set_accept_language(language)

        # this is a compatibility code for esb
        key = "Blueking-Language"
        if language:
            self._set_header(key, language)
        else:
            self._delete_header(key)

    def set_bk_api_ver(
        self,
        bk_api_ver,  # type: str
    ):
        # `bk_api_ver` may be empty, in order to simplify the path rendering, update it to a sub-path,
        # path containing bk_api_ver should be set like this: `/api/c/compapi{bk_api_ver}/demo/test/`
        self.session.path_params["bk_api_ver"] = "/{}".format(bk_api_ver) if bk_api_ver else ""

    def _set_header(
        self,
        key,  # type: str
        value,  # type: str
    ):
        self.session.headers[key] = value

    def _delete_header(
        self,
        key,  # type: str
    ):
        if key in self.session.headers:
            del self.session.headers[key]
