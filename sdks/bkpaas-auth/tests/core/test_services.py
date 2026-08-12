# -*- coding: utf-8 -*-
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured

from bkpaas_auth.core.services import (
    async_get_bk_user_info,
    async_get_rtx_user_info,
    conf,
    get_app_credentials,
)
from tests.utils import mock_json_response


class TestGetRTXUserInfoCredentails:
    def test_when_provided(self, settings):
        with mock.patch.multiple(conf, TOKEN_APP_CODE="foo", TOKEN_SECRET_KEY="bar"):
            assert get_app_credentials() == {"bk_app_code": "foo", "bk_app_secret": "bar"}

    def test_not_provided(self, settings):
        with pytest.raises(ImproperlyConfigured), mock.patch.multiple(
            conf,
            TOKEN_APP_CODE=None,
            TOKEN_SECRET_KEY=None,
        ):
            get_app_credentials()


@pytest.mark.asyncio
@mock.patch("bkpaas_auth.core.services.cache.aset", new_callable=mock.AsyncMock)
@mock.patch("bkpaas_auth.core.services.cache.aget", new_callable=mock.AsyncMock, return_value=None)
@mock.patch("bkpaas_auth.core.services.http_get", side_effect=AssertionError("sync HTTP must not be used"))
@mock.patch("bkpaas_auth.core.services.async_http_get", new_callable=mock.AsyncMock)
async def test_async_get_rtx_user_info_uses_async_cache_and_http(
    async_http_get,
    http_get,
    cache_get,
    cache_set,
    get_rtx_user_info_response,
):
    async_http_get.return_value = mock_json_response(get_rtx_user_info_response)

    user_info = await async_get_rtx_user_info("user1")

    assert user_info.username == "user1"
    cache_get.assert_awaited_once()
    cache_set.assert_awaited_once()
    async_http_get.assert_awaited_once()
    http_get.assert_not_called()


@pytest.mark.asyncio
@mock.patch("bkpaas_auth.core.services.cache.aset", new_callable=mock.AsyncMock)
@mock.patch("bkpaas_auth.core.services.cache.aget", new_callable=mock.AsyncMock)
@mock.patch("bkpaas_auth.core.services.async_http_get", new_callable=mock.AsyncMock)
async def test_async_get_bk_user_info_uses_cached_result(async_http_get, cache_get, cache_set):
    cache_get.return_value = {
        "code": 0,
        "data": {"bk_username": "cached-user", "chname": "Cached User", "email": "", "phone": ""},
    }

    user_info = await async_get_bk_user_info("cached-user")

    assert user_info.username == "cached-user"
    assert user_info.chinese_name == "Cached User"
    async_http_get.assert_not_awaited()
    cache_set.assert_not_awaited()
