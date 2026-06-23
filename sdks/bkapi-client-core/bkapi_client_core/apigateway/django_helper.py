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

from typing import Optional, Type

from bkapi_client_core.client import BaseClient
from bkapi_client_core.config import SettingKeys, settings
from bkapi_client_core.django_helper import get_client_by_request as _get_client_by_request
from bkapi_client_core.django_helper import get_client_by_username as _get_client_by_username


def _get_endpoint(endpoint=None):
    if endpoint:
        return endpoint

    return settings.get(SettingKeys.BK_API_URL_TMPL, "")  # type: ignore


def get_client_by_request(
    client_cls: Type[BaseClient],
    request,
    endpoint: Optional[str] = None,
    stage: Optional[str] = None,
    bk_app_code: Optional[str] = None,
    bk_app_secret: Optional[str] = None,
    accept_language: Optional[str] = None,
):
    """Returns a client according to the current django request

    :param client_cls: client class model
    :param request: django request object, can get authentication information from request cookies
    :param endpoint: api service url
    :param stage: name of apigateway stage
    :param bk_app_code: blueking app code
    :param bk_app_secret: blueking app secret
    :param accept_language: request accept language
    """
    return _get_client_by_request(
        client_cls,
        request,
        endpoint=_get_endpoint(endpoint),
        stage=stage,
        bk_app_code=bk_app_code,
        bk_app_secret=bk_app_secret,
        accept_language=accept_language,
    )


def get_client_by_username(
    client_cls: Type[BaseClient],
    username,
    endpoint: Optional[str] = None,
    stage: Optional[str] = None,
    bk_app_code: Optional[str] = None,
    bk_app_secret: Optional[str] = None,
    accept_language: Optional[str] = None,
):
    """Returns a client according to the current username

    :param client_cls: client class model
    :param username: the current username
    :param endpoint: api service url
    :param stage: name of apigateway stage
    :param bk_app_code: blueking app code
    :param bk_app_secret: blueking app secret
    :param accept_language: request accept language
    """
    return _get_client_by_username(
        client_cls,
        username,
        endpoint=_get_endpoint(endpoint),
        stage=stage,
        bk_app_code=bk_app_code,
        bk_app_secret=bk_app_secret,
        accept_language=accept_language,
    )
