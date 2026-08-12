# -*- coding: utf-8 -*-
from unittest import mock

import pytest
from django.conf import settings

from bkpaas_auth import async_get_user_by_user_id, get_user_by_user_id
from tests.utils import mock_json_response


def test_get_user_by_user_id(get_rtx_user_info_response):
    with mock.patch("httpx2.Client.request") as mocked_request:
        mocked_request.return_value = mock_json_response(get_rtx_user_info_response)

        user = get_user_by_user_id(settings.USER_ID, username_only=True)
        assert user.username == settings.USER_NAME
        assert not user.nickname

        user = get_user_by_user_id(settings.USER_ID, username_only=False)
        assert user.username == settings.USER_NAME
        assert user.nickname == settings.USER_NICKNAME


@pytest.mark.asyncio
@mock.patch("bkpaas_auth.core.services.cache.aset", new_callable=mock.AsyncMock)
@mock.patch("bkpaas_auth.core.services.cache.aget", new_callable=mock.AsyncMock, return_value=None)
@mock.patch("bkpaas_auth.core.services.async_http_get", new_callable=mock.AsyncMock)
async def test_async_get_user_by_user_id(async_http_get, cache_get, cache_set, get_rtx_user_info_response):
    async_http_get.return_value = mock_json_response(get_rtx_user_info_response)

    user = await async_get_user_by_user_id(settings.USER_ID, username_only=False)

    assert user.username == settings.USER_NAME
    assert user.nickname == settings.USER_NICKNAME
    async_http_get.assert_awaited_once()
    cache_get.assert_awaited_once()
    cache_set.assert_awaited_once()
