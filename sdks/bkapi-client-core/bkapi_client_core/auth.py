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
import json
from typing import Dict, Optional

from requests.auth import AuthBase
from requests.models import PreparedRequest


class BKApiAuthorization(AuthBase):
    def __init__(self, **auth):
        self.auth = auth  # type: Dict[str, Optional[str]]

    def update(
        self,
        auth,  # type: Dict[str, Optional[str]]
    ):
        self.auth.update(auth)

    def __call__(
        self,
        request,  # type: PreparedRequest
    ):
        # type: (...) -> PreparedRequest

        # `access_token` can represent app and user,
        # if access_token exists, other authorization parameters are not needed,
        # `jwt` can authenticate user and needs to be used with `access_token`
        if self.auth.get("access_token"):
            authorization = {k: v for k, v in self.auth.items() if v and k in ("access_token", "jwt")}
        else:
            authorization = {k: v for k, v in self.auth.items() if v}

        request.headers["X-Bkapi-Authorization"] = json.dumps(authorization)
        return request
