# -*- coding: utf-8 -*-
"""
http基础方法

Rules:
1. POST/DELETE/PUT: json in
2. GET带参数，HEAD不带参数
3. 所有请求 json out，如果resp.json报错, 则是接口问题
"""

import asyncio
import atexit
import json
import logging
import threading
import weakref
from typing import Any

import httpx2
from django.test.signals import setting_changed

from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.exceptions import HttpRequestError, ServiceError
from bkpaas_auth.utils import scrub_data

logger = logging.getLogger(__name__)

_HTTP_CLIENT_LIMITS = httpx2.Limits(max_connections=20, max_keepalive_connections=20)
# 单次请求总耗时最多 30 秒，其中建立连接最多 5 秒。认证请求处于 Web 请求的关键路径上，
# 必须有明确的超时上限，否则对端 hang 住会一直占用 worker。
_HTTP_CLIENT_TIMEOUT = httpx2.Timeout(30.0, connect=5.0)

_http_client: httpx2.Client | None = None

# 异步客户端按事件循环分别保存，原因见 get_async_http_client() 的文档。使用弱引用字典，
# 事件循环对象被回收后对应的客户端也会自动从字典中移除，避免在“每次调用新建事件循环”
# （如 asgiref.sync.async_to_sync）的场景下无限堆积。
_async_http_clients: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, httpx2.AsyncClient]" = (
    weakref.WeakKeyDictionary()
)
_client_lock = threading.Lock()


def _build_client_kwargs() -> dict[str, Any]:
    """Build the shared keyword arguments for creating httpx clients."""
    return {
        "verify": bkauth_settings.REQUESTS_VERIFY,
        "cert": bkauth_settings.REQUESTS_CERT,
        "timeout": _HTTP_CLIENT_TIMEOUT,
        "follow_redirects": True,
        "limits": _HTTP_CLIENT_LIMITS,
    }


def get_http_client() -> httpx2.Client:
    """Return the shared synchronous client used for connection pooling."""
    global _http_client

    if _http_client is None:
        with _client_lock:
            if _http_client is None:
                _http_client = httpx2.Client(**_build_client_kwargs())
    return _http_client


def get_async_http_client() -> httpx2.AsyncClient:
    """Return the shared asynchronous client bound to the current event loop.

    AsyncClient 内部连接池持有的 socket 与 anyio 锁都和“创建连接时所在的事件循环”强绑定，
    一旦换到另一个事件循环去复用池中的 keep-alive 连接，就会抛出
    "RuntimeError: Event loop is closed"。因此这里不能像同步客户端那样用进程级单例，
    必须按事件循环分别缓存。

    典型的多事件循环场景：
    - 在 WSGI / Celery / management command 中通过 asgiref.sync.async_to_sync 调用本模块的
      异步接口，每次调用都可能是一个新的事件循环；
    - 下游项目用 pytest-asyncio 写测试，默认每个用例一个新的事件循环。
    """
    loop = asyncio.get_running_loop()

    client = _async_http_clients.get(loop)
    if client is None:
        # 加锁是为了保护多个线程各自持有事件循环时对弱引用字典的并发写入，
        # 同一事件循环内部是单线程的，不存在竞争。
        with _client_lock:
            client = _async_http_clients.get(loop)
            if client is None:
                client = httpx2.AsyncClient(**_build_client_kwargs())
                _async_http_clients[loop] = client
    return client


def reset_http_clients() -> None:
    """Discard the cached clients so that the next request picks up the latest settings.

    这里只丢弃引用而不主动 close()：可能有其他线程/协程正在使用旧客户端，强行关闭会打断
    进行中的请求。丢弃后旧客户端会在引用计数归零时被回收，连接随之释放。
    """
    global _http_client

    with _client_lock:
        _http_client = None
        _async_http_clients.clear()


def _reset_http_clients_on_setting_changed(*args, **kwargs) -> None:
    # 只有 SSL 相关配置会影响已创建的客户端，其余配置在每次请求时读取，无需重建。
    if kwargs.get("setting") in ("BKAUTH_REQUESTS_VERIFY", "BKAUTH_REQUESTS_CERT"):
        reset_http_clients()


setting_changed.connect(_reset_http_clients_on_setting_changed)


@atexit.register
def _close_http_client_at_exit() -> None:
    """Close the synchronous client at interpreter exit to release pooled sockets.

    异步客户端不在这里关闭：关闭它需要一个正在运行的事件循环，而进程退出时已经没有了。
    它们保存在以事件循环为键的弱引用字典中，事件循环被回收后即可一并回收。
    """
    global _http_client

    client, _http_client = _http_client, None
    if client is not None:
        client.close()


def build_req_details_str(
    method: str,
    url: str | httpx2.URL,
    params: Any,
    data: Any,
    headers: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str:
    """Build the request details string for logging purpose."""
    msg = f"{method} {url}"
    if params:
        msg += f", params: {scrub_data(params)}"
    if data:
        msg += f", data: {scrub_data(data)}"
    if headers:
        msg += f", headers: {scrub_data(headers)}"
    msg += f", kwargs: {kwargs}"
    return msg


def _prepare_request(method: str, url: str | httpx2.URL, kwargs: dict[str, Any]) -> tuple[Any, Any, str]:
    params = kwargs.pop("params", None)
    data = kwargs.pop("data", None)

    req_details = build_req_details_str(method, url, params, data, **kwargs)
    logger.debug("Sending HTTP request, req details: %s", req_details)
    return params, data, req_details


# 一并捕获以保持“非法 URL 统一转成 HttpRequestError”的对外行为。
_REQUEST_ERRORS = (httpx2.RequestError, httpx2.InvalidURL, TypeError)


def _http_request(method: str, url: str | httpx2.URL, **kwargs) -> httpx2.Response:
    params, data, req_details = _prepare_request(method, url, kwargs)

    try:
        resp = get_http_client().request(method, url, params=params, data=data, **kwargs)
    except _REQUEST_ERRORS as e:
        logger.exception("http request error! req details: %s", req_details)
        raise HttpRequestError(f"http request error: {e}") from e

    return resp


async def _async_http_request(method: str, url: str | httpx2.URL, **kwargs) -> httpx2.Response:
    params, data, req_details = _prepare_request(method, url, kwargs)

    try:
        resp = await get_async_http_client().request(method, url, params=params, data=data, **kwargs)
    except _REQUEST_ERRORS as e:
        logger.exception("http request error! req details: %s", req_details)
        raise HttpRequestError(f"http request error: {e}") from e

    return resp


def resp_to_json(resp: httpx2.Response) -> dict[str, Any] | list[Any]:
    try:
        return resp.json()
    except json.decoder.JSONDecodeError:
        logger.exception(
            "response json error! response.status_code: %s, response.text: %s",
            resp.status_code,
            resp.text,
        )
        raise ServiceError("parse json response error")


def http_get(url: str | httpx2.URL, **kwargs) -> httpx2.Response:
    return _http_request(method="GET", url=url, **kwargs)


async def async_http_get(url: str | httpx2.URL, **kwargs) -> httpx2.Response:
    return await _async_http_request(method="GET", url=url, **kwargs)
