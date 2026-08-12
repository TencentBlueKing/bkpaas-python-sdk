from unittest import mock

import pytest
from django.contrib import auth

from bkpaas_auth.monkey import aget_user


@pytest.mark.asyncio
async def test_async_get_user_passes_request_to_backend():
    request = mock.MagicMock()
    session_values = {
        auth.SESSION_KEY: "user-id",
        auth.BACKEND_SESSION_KEY: "tests.backends.AsyncBackend",
    }
    request.session.aget = mock.AsyncMock(side_effect=session_values.__getitem__)
    expected_user = mock.MagicMock()
    backend = mock.MagicMock()
    backend.aget_user = mock.AsyncMock(return_value=expected_user)

    with mock.patch("bkpaas_auth.monkey.auth.load_backend", return_value=backend):
        user = await aget_user(request)

    assert user is expected_user
    assert backend.request is request
    backend.aget_user.assert_awaited_once_with("user-id")


@pytest.mark.asyncio
async def test_async_get_user_returns_anonymous_user_without_session():
    request = mock.MagicMock()
    request.session.aget = mock.AsyncMock(side_effect=KeyError)

    user = await aget_user(request)

    assert user.is_anonymous


@pytest.mark.asyncio
async def test_async_get_user_returns_anonymous_user_for_missing_session_values():
    request = mock.MagicMock()
    request.session.aget = mock.AsyncMock(return_value=None)

    user = await aget_user(request)

    assert user.is_anonymous
