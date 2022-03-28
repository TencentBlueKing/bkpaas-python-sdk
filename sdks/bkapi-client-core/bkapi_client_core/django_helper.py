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
import logging
from typing import Optional, Type

from bkapi_client_core.client import BaseClient
from bkapi_client_core.config import SettingKeys, settings
from bkapi_client_core.exceptions import UserNotAuthenticated

try:
    import bkoauth
except ImportError:
    bkoauth = None

logger = logging.getLogger(__name__)


def _get_client_by_settings(
    client_cls,  # type: Type[BaseClient]
    bk_app_code=None,  # type: Optional[str]
    bk_app_secret=None,  # type: Optional[str]
    **kwargs
):
    """Returns a client according to the django settings"""
    client = client_cls(**kwargs)

    client.update_bkapi_authorization(
        bk_app_code=bk_app_code or settings.get(SettingKeys.APP_CODE),
        bk_app_secret=bk_app_secret or settings.get(SettingKeys.APP_SECRET),
    )

    # disable global https verify
    if settings.get(SettingKeys.BK_API_CLIENT_ENABLE_SSL_VERIFY):
        client.disable_ssl_verify()

    return client


def _validate_user_authenticated(user):
    is_authenticated = user.is_authenticated
    if callable(is_authenticated):
        is_authenticated = is_authenticated()
    if not is_authenticated:
        raise UserNotAuthenticated(user)


def _get_authorization_from_cookies(request, cookie_name_to_key):
    return {
        key: request.COOKIES.get(cookie_name) or request.session.get(cookie_name)
        for cookie_name, key in cookie_name_to_key.items()
    }


def get_client_by_request(
    client_cls,  # type: Type[BaseClient]
    request,
    **kwargs
):
    """Returns a client according to the current request"""

    def get_access_token():
        if not bkoauth:
            return None
        try:
            token = bkoauth.get_access_token(request)
            return token.access_token
        except Exception:
            logger.warning("get access_token by request failed")

    _validate_user_authenticated(request.user)

    client = _get_client_by_settings(client_cls, **kwargs)

    authorization = {"access_token": get_access_token(), "bk_username": request.user.username}
    authorization.update(
        _get_authorization_from_cookies(
            request,
            settings.get(SettingKeys.BK_API_AUTHORIZATION_COOKIES_MAPPING) or {},
        )
    )
    client.update_bkapi_authorization(**authorization)

    return client


def get_client_by_username(
    client_cls,  # type: Type[BaseClient]
    username,  # type: str
    **kwargs
):
    """Returns a client according to the username"""

    def get_access_token():
        if not bkoauth:
            return None
        try:
            token = bkoauth.get_access_token_by_user(username)
            return token.access_token
        except Exception:
            logger.warning("get access_token by request failed")

    client = _get_client_by_settings(client_cls, **kwargs)
    client.update_bkapi_authorization(access_token=get_access_token(), bk_username=username)

    return client
