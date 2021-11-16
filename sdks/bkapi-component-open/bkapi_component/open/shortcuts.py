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
from bkapi_client_core.esb import generic_type_partial as _partial
from bkapi_client_core.esb.django_helper import get_client_by_request as _get_client_by_request
from bkapi_client_core.esb.django_helper import get_client_by_username as _get_client_by_username
from bkapi_client_core.esb.django_helper import get_client_by_user as _get_client_by_user

from .client import Client

get_client_by_request = _partial(Client, _get_client_by_request)
get_client_by_username = _partial(Client, _get_client_by_username)
get_client_by_user = _partial(Client, _get_client_by_user)
