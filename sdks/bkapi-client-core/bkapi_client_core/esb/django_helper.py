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
from typing import Optional, Type

from bkapi_client_core.client import BaseClient
from bkapi_client_core.config import SettingKeys, settings
from bkapi_client_core.django_helper import get_client_by_request as _get_client_by_request
from bkapi_client_core.django_helper import get_client_by_username as _get_client_by_username

_bk_api_use_test_env = False


def _get_endpoint(endpoint=None):
    if endpoint:
        return endpoint
    return settings.get(SettingKeys.BK_COMPONENT_API_URL, "")


def _get_default_language():
    try:
        from django.utils import translation

        return translation.get_language()
    except ImportError:
        return None


def get_client_by_request(
    client_cls,  # type: Type[BaseClient]
    request,
    endpoint=None,  # type: Optional[str]
    bk_app_code=None,  # type: Optional[str]
    bk_app_secret=None,  # type: Optional[str]
):
    """Returns a client according to the current django request

    :param client_cls: client class model
    :param request: django request object, can get authentication information from request cookies
    :param endpoint: api service url
    :param bk_app_code: blueking app code
    :param bk_app_secret: blueking app secret
    """
    return _get_client_by_request(
        client_cls,
        request,
        endpoint=_get_endpoint(endpoint),
        bk_app_code=bk_app_code,
        bk_app_secret=bk_app_secret,
        bk_api_ver=settings.get(SettingKeys.DEFAULT_BK_API_VER),
        use_test_env=settings.get(SettingKeys.BK_API_USE_TEST_ENV),
        language=_get_default_language(),
    )


def get_client_by_username(
    client_cls,  # type: Type[BaseClient]
    username,
    endpoint=None,  # type: Optional[str]
    bk_app_code=None,  # type: Optional[str]
    bk_app_secret=None,  # type: Optional[str]
):
    """Returns a client according to the current username

    :param client_cls: client class model
    :param username: the current username
    :param endpoint: api service url
    :param bk_app_code: blueking app code
    :param bk_app_secret: blueking app secret
    """
    return _get_client_by_username(
        client_cls,
        username,
        endpoint=_get_endpoint(endpoint),
        bk_app_code=bk_app_code,
        bk_app_secret=bk_app_secret,
        bk_api_ver=settings.get(SettingKeys.DEFAULT_BK_API_VER),
        use_test_env=settings.get(SettingKeys.BK_API_USE_TEST_ENV),
        language=_get_default_language(),
    )


def get_client_by_user(
    client_cls,  # type: Type[BaseClient]
    user,
    endpoint=None,  # type: Optional[str]
    bk_app_code=None,  # type: Optional[str]
    bk_app_secret=None,  # type: Optional[str]
):
    """Returns a client according to the current user

    :param client_cls: client class model
    :param user: the current user
    :param endpoint: api service url
    :param bk_app_code: blueking app code
    :param bk_app_secret: blueking app secret
    """
    username = getattr(user, "username", user)
    return get_client_by_username(client_cls, username, endpoint, bk_app_code, bk_app_secret)
