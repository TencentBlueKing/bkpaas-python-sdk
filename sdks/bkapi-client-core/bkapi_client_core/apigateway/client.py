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
from typing import Optional

from bkapi_client_core.client import BaseClient
from bkapi_client_core.config import SettingKeys, settings
from bkapi_client_core.session import Session
from bkapi_client_core.utils import urljoin


class APIGatewayClient(BaseClient):
    _default_stage = "prod"
    _api_name = ""

    def __init__(
        self,
        stage=None,  # type: Optional[str]
        endpoint="",  # type: str
        session=None,  # type: Optional[Session]
    ):
        # Stage is allowed to be an empty string, because the endpoint may already contain stage
        if stage is not None:
            self._stage = stage
        else:
            stage_mappings = settings.get(SettingKeys.DEFAULT_STAGE_MAPPINGS) or {}
            self._stage = stage_mappings.get(self._api_name, self._default_stage)

        # The path of the APIGateway API contains stage name,
        # so, add it to endpoint as a path variable, in order to switch stage
        endpoint = urljoin(endpoint, "/{stage_name}")
        super(APIGatewayClient, self).__init__(endpoint, session)

    def _get_endpoint(self):
        # type: (...) -> str

        # In order to prevent `api_name`, `stage_name` from conflicting with other path variables,
        # render the endpoint first.
        return self._endpoint.format(api_name=self._api_name, stage_name=self._stage)
