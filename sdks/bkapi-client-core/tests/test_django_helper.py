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
import pytest

from bkapi_client_core import django_helper
from bkapi_client_core.exceptions import UserNotAuthenticated


@pytest.fixture
def django_settings(settings):
    return settings


@pytest.fixture
def client_cls(mocker):
    return mocker.MagicMock()


@pytest.fixture
def django_request(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_get_client_by_settings(mocker):
    return mocker.patch.object(django_helper, "_get_client_by_settings")


@pytest.fixture
def mock_validate_user_authenticated(mocker):
    return mocker.patch.object(django_helper, "_validate_user_authenticated")


@pytest.mark.parametrize(
    "app_code_passed,app_secret_passed,app_code_in_settings,app_secret_in_settings",
    [
        (False, False, True, True),
        (True, True, False, False),
        (False, False, False, False),
        (True, True, True, True),
        (False, True, True, False),
        (True, False, False, True),
    ],
)
def test_get_client_by_settings(
    django_settings,
    faker,
    client_cls,
    app_code_passed,
    app_secret_passed,
    app_code_in_settings,
    app_secret_in_settings,
):
    django_settings.APP_CODE = faker.pystr() if app_code_in_settings else None
    django_settings.SECRET_KEY = faker.pystr() if app_secret_in_settings else None
    django_settings.BK_APP_CODE = django_settings.APP_CODE
    django_settings.BK_APP_SECRET = django_settings.SECRET_KEY

    bk_app_code = faker.pystr() if app_code_passed else ""
    bk_app_secret = faker.pystr() if app_secret_passed else ""

    excepted_app_code = bk_app_code or django_settings.APP_CODE
    excepted_app_secret = bk_app_secret or django_settings.SECRET_KEY

    endpoint = faker.pystr()

    client = django_helper._get_client_by_settings(
        client_cls, bk_app_code=bk_app_code, bk_app_secret=bk_app_secret, endpoint=endpoint
    )
    client_cls.assert_called_once_with(endpoint=endpoint)
    client.update_bkapi_authorization.assert_called_once_with(
        bk_app_code=excepted_app_code, bk_app_secret=excepted_app_secret
    )


@pytest.mark.parametrize("is_authenticated", [True, lambda: True])
def test_vaildate_user_authenticated(django_request, is_authenticated):
    django_request.user.is_authenticated = is_authenticated
    django_helper._validate_user_authenticated(django_request.user)


@pytest.mark.parametrize("is_authenticated", [False, lambda: False])
def test_vaildate_user_authenticated_error(django_request, is_authenticated):
    django_request.user.is_authenticated = is_authenticated
    with pytest.raises(UserNotAuthenticated):  # type: ignore
        django_helper._validate_user_authenticated(django_request.user)


@pytest.mark.parametrize(
    "cookies, session, cookie_name_to_key, expected",
    [
        ({"color": "red"}, {}, {"color": "color"}, {"color": "red"}),
        ({"color": "red"}, {}, {"color": "color_name"}, {"color_name": "red"}),
        ({}, {"color": "red"}, {"color": "color_name"}, {"color_name": "red"}),
        ({"color": "red"}, {"color": "green"}, {"color": "color"}, {"color": "red"}),
        ({}, {}, {"color": "color"}, {"color": None}),
    ],
)
def test_get_authorization_from_cookies(mocker, cookies, session, cookie_name_to_key, expected):
    request = mocker.MagicMock(COOKIES=cookies, session=session)
    assert django_helper._get_authorization_from_cookies(request, cookie_name_to_key) == expected


@pytest.mark.parametrize(
    "bkoauth,authorization_in_cookies,expected_access_token",
    [
        (None, {}, None),
        ({"get_access_token.return_value.access_token": "test_token"}, {}, "test_token"),
        ({"get_access_token.side_effect": ValueError}, {}, None),
        ({"get_access_token.return_value.access_token": "test"}, {"x-token": "test"}, "test"),
    ],
)
def test_get_client_by_request(
    mocker,
    faker,
    client_cls,
    django_request,
    mock_get_client_by_settings,
    mock_validate_user_authenticated,
    bkoauth,
    authorization_in_cookies,
    expected_access_token,
):
    mocker.patch.object(django_helper, "bkoauth", bkoauth and mocker.MagicMock(**bkoauth))
    mocker.patch.object(django_helper, "_get_authorization_from_cookies", return_value=authorization_in_cookies)

    django_request.user.username = "admin"
    django_request.user.is_authenticated = True
    endpoint = faker.pystr()

    client = django_helper.get_client_by_request(client_cls, django_request, endpoint=endpoint)
    mock_validate_user_authenticated.assert_called_once_with(django_request.user)
    mock_get_client_by_settings.assert_called_once_with(client_cls, endpoint=endpoint)
    client.update_bkapi_authorization.assert_called_once_with(
        **dict({"access_token": expected_access_token, "bk_username": "admin"}, **authorization_in_cookies)
    )


@pytest.mark.parametrize(
    "bkoauth,expected_access_token",
    [
        (None, None),
        ({"get_access_token_by_user.return_value.access_token": "test_token"}, "test_token"),
        ({"get_access_token_by_user.side_effect": ValueError}, None),
    ],
)
def test_get_client_by_username(
    mocker,
    faker,
    client_cls,
    django_request,
    mock_get_client_by_settings,
    bkoauth,
    expected_access_token,
):
    mocker.patch.object(django_helper, "bkoauth", bkoauth and mocker.MagicMock(**bkoauth))

    endpoint = faker.pystr()

    client = django_helper.get_client_by_username(client_cls, "test", endpoint=endpoint)
    mock_get_client_by_settings.assert_called_once_with(client_cls, endpoint=endpoint)
    client.update_bkapi_authorization.assert_called_once_with(access_token=expected_access_token, bk_username="test")
