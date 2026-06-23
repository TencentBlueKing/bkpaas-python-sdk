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

import json
from typing import Dict, Optional

from requests.auth import AuthBase
from requests.models import PreparedRequest


class BKApiAuthorization(AuthBase):
    def __init__(self, **auth):
        self.auth: Dict[str, Optional[str]] = auth

    def update(self, auth: Dict[str, Optional[str]]):
        self.auth.update(auth)

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        # `access_token` can represent app and user,
        # if access_token exists, other authorization parameters are not needed,
        # `jwt` can authenticate user and needs to be used with `access_token`
        if self.auth.get("access_token"):
            authorization = {k: v for k, v in self.auth.items() if v and k in ("access_token", "jwt")}
        else:
            authorization = {k: v for k, v in self.auth.items() if v}

        request.headers["X-Bkapi-Authorization"] = json.dumps(authorization)
        return request
