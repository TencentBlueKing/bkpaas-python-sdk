# -*- coding: utf-8 -*-
from unittest import mock

import httpx2
import pytest

from bkpaas_auth.core.exceptions import HttpRequestError, ServiceError
from bkpaas_auth.core import http
from bkpaas_auth.core.http import async_http_get, get_async_http_client, get_http_client, http_get, resp_to_json


def test_get_http_client_reuses_configured_client():
    with mock.patch.object(http, "_http_client", None), mock.patch("httpx2.Client") as client_class:
        client = get_http_client()

        assert get_http_client() is client

    client_class.assert_called_once_with(
        verify=False,
        cert=None,
        timeout=None,
        follow_redirects=True,
        limits=http._HTTP_CLIENT_LIMITS,
    )


def test_get_async_http_client_reuses_configured_client():
    with mock.patch.object(http, "_async_http_client", None), mock.patch("httpx2.AsyncClient") as client_class:
        client = get_async_http_client()

        assert get_async_http_client() is client

    client_class.assert_called_once_with(
        verify=False,
        cert=None,
        timeout=None,
        follow_redirects=True,
        limits=http._HTTP_CLIENT_LIMITS,
    )


def test_http_get_uses_sync_client():
    expected_response = httpx2.Response(200, json={"result": True})

    with mock.patch("httpx2.Client.request", return_value=expected_response) as mocked_request:
        response = http_get("https://example.com/user", params={"username": "admin"}, timeout=10)

    assert response is expected_response
    mocked_request.assert_called_once_with(
        "GET",
        "https://example.com/user",
        params={"username": "admin"},
        data=None,
        timeout=10,
    )


@pytest.mark.asyncio
async def test_async_http_get_uses_async_client():
    expected_response = httpx2.Response(200, json={"result": True})

    with mock.patch(
        "httpx2.AsyncClient.request",
        new_callable=mock.AsyncMock,
        return_value=expected_response,
    ) as mocked_request:
        response = await async_http_get(
            "https://example.com/user",
            params={"username": "admin"},
            timeout=10,
        )

    assert response is expected_response
    mocked_request.assert_awaited_once_with(
        "GET",
        "https://example.com/user",
        params={"username": "admin"},
        data=None,
        timeout=10,
    )


@pytest.mark.parametrize(
    "error",
    [httpx2.ConnectError("connection failed"), httpx2.InvalidURL("invalid URL")],
)
def test_http_get_translates_httpx2_errors(error):
    with mock.patch("httpx2.Client.request", side_effect=error), pytest.raises(
        HttpRequestError,
        match=f"http request error: {error}",
    ):
        http_get("https://example.com/user")


@pytest.mark.asyncio
async def test_async_http_get_translates_httpx2_errors():
    with mock.patch(
        "httpx2.AsyncClient.request",
        new_callable=mock.AsyncMock,
        side_effect=httpx2.ConnectError("connection failed"),
    ), pytest.raises(HttpRequestError, match="http request error: connection failed"):
        await async_http_get("https://example.com/user")


def test_http_get_translates_invalid_url_type():
    with pytest.raises(HttpRequestError, match="http request error: invalid URL type: NoneType"):
        http_get(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_async_http_get_translates_invalid_url_type():
    with pytest.raises(HttpRequestError, match="http request error: invalid URL type: NoneType"):
        await async_http_get(None)  # type: ignore[arg-type]


def test_resp_to_json():
    assert resp_to_json(httpx2.Response(200, json={"result": True})) == {"result": True}


def test_resp_to_json_rejects_invalid_json():
    response = httpx2.Response(200, text="not-json")

    with pytest.raises(ServiceError, match="parse json response error"):
        resp_to_json(response)
