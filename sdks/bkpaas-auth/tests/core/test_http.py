# -*- coding: utf-8 -*-
import asyncio
import gc
import weakref
from unittest import mock

import httpx2
import pytest
from django.test.utils import override_settings

from bkpaas_auth.core import http
from bkpaas_auth.core.exceptions import HttpRequestError, ServiceError
from bkpaas_auth.core.http import (
    async_http_get,
    build_req_details_str,
    get_async_http_client,
    get_http_client,
    http_get,
    resp_to_json,
)

EXPECTED_CLIENT_KWARGS = {
    "verify": False,
    "cert": None,
    "timeout": http._HTTP_CLIENT_TIMEOUT,
    "follow_redirects": True,
    "limits": http._HTTP_CLIENT_LIMITS,
}


@pytest.fixture
def isolated_clients():
    """Isolate the module level client caches so a test never leaks into another one."""
    with mock.patch.object(http, "_http_client", None), mock.patch.object(
        http, "_async_http_clients", weakref.WeakKeyDictionary()
    ):
        yield


def test_client_timeout_is_bounded():
    """认证请求位于关键路径上，必须有明确的超时上限"""
    assert http._HTTP_CLIENT_TIMEOUT.read == 30.0
    assert http._HTTP_CLIENT_TIMEOUT.connect == 5.0


def test_get_http_client_reuses_configured_client(isolated_clients):
    with mock.patch("httpx2.Client") as client_class:
        client = get_http_client()

        assert get_http_client() is client

    client_class.assert_called_once_with(**EXPECTED_CLIENT_KWARGS)


@pytest.mark.asyncio
async def test_get_async_http_client_reuses_configured_client(isolated_clients):
    with mock.patch("httpx2.AsyncClient") as client_class:
        client = get_async_http_client()

        assert get_async_http_client() is client

    client_class.assert_called_once_with(**EXPECTED_CLIENT_KWARGS)


def test_get_async_http_client_is_created_per_event_loop(isolated_clients):
    """AsyncClient 的连接池与事件循环绑定，跨 loop 复用会抛 "Event loop is closed"。"""
    clients = []

    async def collect_client():
        clients.append(get_async_http_client())

    asyncio.run(collect_client())
    asyncio.run(collect_client())

    assert len(clients) == 2
    assert clients[0] is not clients[1]


def test_async_clients_are_released_with_their_event_loop(isolated_clients):
    async def touch_client():
        get_async_http_client()

    asyncio.run(touch_client())
    gc.collect()

    # 事件循环被回收后，弱引用字典中对应的客户端也应随之消失
    assert len(http._async_http_clients) == 0


def test_clients_are_rebuilt_after_ssl_settings_changed(isolated_clients):
    # side_effect 让每次构造都返回不同的实例，否则 MagicMock 的 return_value 是单例
    with mock.patch("httpx2.Client", side_effect=lambda **kwargs: mock.MagicMock()) as client_class:
        first_client = get_http_client()

        with override_settings(BKAUTH_REQUESTS_VERIFY=True):
            second_client = get_http_client()

    assert first_client is not second_client
    assert client_class.call_args_list[0].kwargs["verify"] is False
    assert client_class.call_args_list[1].kwargs["verify"] is True


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
    with pytest.raises(HttpRequestError, match="http request error: Invalid type for url"):
        http_get(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_async_http_get_translates_invalid_url_type():
    with pytest.raises(HttpRequestError, match="http request error: Invalid type for url"):
        await async_http_get(None)  # type: ignore[arg-type]


def test_build_req_details_str_scrubs_sensitive_headers():
    """X-Bkapi-Authorization 里含有应用密钥和用户票据，不能明文出现在日志中"""
    msg = build_req_details_str(
        "GET",
        "https://example.com/user",
        params={"bk_token": "s3cr3t-token"},
        data=None,
        headers={"X-Bkapi-Authorization": '{"bk_app_secret": "s3cr3t-key"}', "blueking-language": "zh-cn"},
    )

    assert "s3cr3t-key" not in msg
    assert "s3cr3t-token" not in msg
    # 非敏感字段应当保留，否则日志失去排查价值
    assert "blueking-language" in msg


def test_resp_to_json():
    assert resp_to_json(httpx2.Response(200, json={"result": True})) == {"result": True}


def test_resp_to_json_rejects_invalid_json():
    response = httpx2.Response(200, text="not-json")

    with pytest.raises(ServiceError, match="parse json response error"):
        resp_to_json(response)
