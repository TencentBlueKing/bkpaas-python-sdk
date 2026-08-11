# -*- coding: utf-8 -*-
"""
http基础方法

Rules:
1. POST/DELETE/PUT: json in
2. GET带参数，HEAD不带参数
3. 所有请求 json out，如果resp.json报错, 则是接口问题
"""

import json
import logging
import threading
from typing import Any, Union

import httpx2

from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.exceptions import HttpRequestError, ServiceError
from bkpaas_auth.utils import scrub_data

logger = logging.getLogger(__name__)

_HTTP_CLIENT_LIMITS = httpx2.Limits(max_connections=20, max_keepalive_connections=20)
_http_client: httpx2.Client | None = None
_async_http_client: httpx2.AsyncClient | None = None
_client_lock = threading.Lock()


def get_http_client() -> httpx2.Client:
    """Return the shared synchronous client used for connection pooling."""
    global _http_client

    if _http_client is None:
        with _client_lock:
            if _http_client is None:
                _http_client = httpx2.Client(
                    verify=bkauth_settings.REQUESTS_VERIFY,
                    cert=bkauth_settings.REQUESTS_CERT,
                    timeout=None,
                    follow_redirects=True,
                    limits=_HTTP_CLIENT_LIMITS,
                )
    return _http_client


def get_async_http_client() -> httpx2.AsyncClient:
    """Return the shared asynchronous client used for connection pooling."""
    global _async_http_client

    if _async_http_client is None:
        with _client_lock:
            if _async_http_client is None:
                _async_http_client = httpx2.AsyncClient(
                    verify=bkauth_settings.REQUESTS_VERIFY,
                    cert=bkauth_settings.REQUESTS_CERT,
                    timeout=None,
                    follow_redirects=True,
                    limits=_HTTP_CLIENT_LIMITS,
                )
    return _async_http_client


def build_req_details_str(method, url, params, data, **kwargs) -> str:
    """Build the request details string for logging purpose."""
    msg = f"{method} {url}"
    if params:
        msg += f", params: {scrub_data(params)}"
    if data:
        msg += f", data: {scrub_data(data)}"
    msg += f", kwargs: {kwargs}"
    return msg


def _prepare_request(method: str, url: str | httpx2.URL, kwargs: dict) -> tuple[Any, Any, str]:
    params = kwargs.pop("params", None)
    data = kwargs.pop("data", None)

    req_details = build_req_details_str(method, url, params, data, **kwargs)
    logger.debug("Sending HTTP request, req details: %s", req_details)
    if not isinstance(url, (str, httpx2.URL)):
        logger.error("http request error! req details: %s", req_details)
        raise HttpRequestError(f"http request error: invalid URL type: {type(url).__name__}")
    return params, data, req_details


def _http_request(method: str, url: str | httpx2.URL, **kwargs) -> httpx2.Response:
    params, data, req_details = _prepare_request(method, url, kwargs)

    try:
        resp = get_http_client().request(method, url, params=params, data=data, **kwargs)
    except (httpx2.RequestError, httpx2.InvalidURL) as e:
        logger.exception("http request error! req details: %s", req_details)
        raise HttpRequestError(f"http request error: {e}") from e

    return resp


async def _async_http_request(method: str, url: str | httpx2.URL, **kwargs) -> httpx2.Response:
    params, data, req_details = _prepare_request(method, url, kwargs)

    try:
        resp = await get_async_http_client().request(method, url, params=params, data=data, **kwargs)
    except (httpx2.RequestError, httpx2.InvalidURL) as e:
        logger.exception("http request error! req details: %s", req_details)
        raise HttpRequestError(f"http request error: {e}") from e

    return resp


def resp_to_json(resp: httpx2.Response) -> Union[dict, list]:
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
