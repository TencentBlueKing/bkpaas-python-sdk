# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

from bkpaas_auth.conf import bkauth_settings as conf
from bkpaas_auth.conf import require_setting
from bkpaas_auth.core.exceptions import HttpRequestError, ServiceError
from bkpaas_auth.core.http import async_http_get, http_get, resp_to_json
from bkpaas_auth.core.user_info import BkUserInfo, RtxUserInfo, UserInfo
from bkpaas_auth.utils import scrub_data

logger = logging.getLogger(__name__)

TUserInfo = TypeVar("TUserInfo", bound=UserInfo)
ResponseOkChecker = Callable[[dict[str, Any]], bool]


def get_app_credentials() -> dict[str, str]:
    """Get app credentials to verify app, which is required for requesting user info API"""
    if conf.TOKEN_APP_CODE and conf.TOKEN_SECRET_KEY:
        return {"bk_app_code": conf.TOKEN_APP_CODE, "bk_app_secret": conf.TOKEN_SECRET_KEY}
    raise ImproperlyConfigured("BKAUTH_TOKEN_APP_CODE and BKAUTH_TOKEN_SECRET_KEY not set")


def get_rtx_user_info(username: str) -> RtxUserInfo | None:
    """Get RTX user info by given RTX username. For better performance, this function
    will try to cache the result for 86400 seconds(1 day).

    :param str username: RTX username
    """

    cache_key = f"bkauth::rests::get_rtx_user_info::{username}"
    result = _get_and_cache_user_info(cache_key, {"login_name": username}, _rtx_response_ok)
    return _make_user_info(result, _rtx_response_ok, RtxUserInfo)


async def async_get_rtx_user_info(username: str) -> RtxUserInfo | None:
    """Asynchronously get RTX user info, using the asynchronous cache and HTTP clients."""
    cache_key = f"bkauth::rests::get_rtx_user_info::{username}"
    result = await _async_get_and_cache_user_info(cache_key, {"login_name": username}, _rtx_response_ok)
    return _make_user_info(result, _rtx_response_ok, RtxUserInfo)


def get_bk_user_info(username: str) -> BkUserInfo | None:
    """Get BK user info by given BK username. For better performance, this function
    will try to cache the result for 86400 seconds(1 day).

    :param str username: BK username
    """

    cache_key = f"bkauth::rests::get_bk_user_info::{username}"
    result = _get_and_cache_user_info(cache_key, {"bk_username": username}, _bk_response_ok)
    return _make_user_info(result, _bk_response_ok, BkUserInfo)


async def async_get_bk_user_info(username: str) -> BkUserInfo | None:
    """Asynchronously get BK user info, using the asynchronous cache and HTTP clients."""
    cache_key = f"bkauth::rests::get_bk_user_info::{username}"
    result = await _async_get_and_cache_user_info(cache_key, {"bk_username": username}, _bk_response_ok)
    return _make_user_info(result, _bk_response_ok, BkUserInfo)


def _get_user_info_request_params(user_params: dict[str, str]) -> dict[str, Any]:
    return {
        "headers": {
            "X-Bkapi-Authorization": json.dumps(dict(user_params, **get_app_credentials())),
        },
        "params": user_params,
    }


def _parse_user_info_response(
    resp: Any, user_params: dict[str, str], response_ok_checker: ResponseOkChecker
) -> dict[str, Any] | None:
    result = resp_to_json(resp)

    if not isinstance(result, dict):
        raise ValueError(f"response type expect dict, got: {result}")  # noqa: TRY004

    if not response_ok_checker(result):
        logger.error(
            f"Get user info fail, url: {conf.TOKEN_USER_INFO_ENDPOINT}, params: {scrub_data(user_params)}"
            f", response: {result}",
        )
        return None
    return result


def _get_cached_user_info(cache_key: str) -> Any:
    try:
        return cache.get(cache_key)
    except Exception as e:
        # Cache is not usable due to some reason including different pickle protocols
        # between different Python versions.
        logger.warning(f"unable to get user info from cache: {e}")
        return None


async def _async_get_cached_user_info(cache_key: str) -> Any:
    try:
        return await cache.aget(cache_key)
    except Exception as e:
        logger.warning(f"unable to get user info from cache: {e}")
        return None


def _fetch_user_info(user_params: dict[str, str], response_ok_checker: ResponseOkChecker) -> dict[str, Any] | None:
    try:
        endpoint = require_setting(conf.TOKEN_USER_INFO_ENDPOINT, "BKAUTH_TOKEN_USER_INFO_ENDPOINT")
        resp = http_get(endpoint, **_get_user_info_request_params(user_params))
    except HttpRequestError:
        raise ServiceError("Unable to get user info") from None
    return _parse_user_info_response(resp, user_params, response_ok_checker)


async def _async_fetch_user_info(
    user_params: dict[str, str], response_ok_checker: ResponseOkChecker
) -> dict[str, Any] | None:
    try:
        endpoint = require_setting(conf.TOKEN_USER_INFO_ENDPOINT, "BKAUTH_TOKEN_USER_INFO_ENDPOINT")
        resp = await async_http_get(endpoint, **_get_user_info_request_params(user_params))
    except HttpRequestError:
        raise ServiceError("Unable to get user info") from None
    return _parse_user_info_response(resp, user_params, response_ok_checker)


def _get_and_cache_user_info(
    cache_key: str, user_params: dict[str, str], response_ok_checker: ResponseOkChecker
) -> dict[str, Any] | None:
    """Get user info from cache, or fetch from API and cache.

    :param dict user_params: username param key to username map, it may be different in different systems
    :param callable response_ok_checker: determine get user is successful
    """
    cached_result = _get_cached_user_info(cache_key)
    if cached_result:
        return cached_result

    result = _fetch_user_info(user_params, response_ok_checker)
    if result is None:
        return None

    # 获取用户信息成后才缓存数据
    cache.set(cache_key, result, timeout=86400)
    return result


async def _async_get_and_cache_user_info(
    cache_key: str, user_params: dict[str, str], response_ok_checker: ResponseOkChecker
) -> dict[str, Any] | None:
    """Asynchronous version of :func:`_get_and_cache_user_info`."""
    cached_result = await _async_get_cached_user_info(cache_key)
    if cached_result:
        return cached_result

    result = await _async_fetch_user_info(user_params, response_ok_checker)
    if result is None:
        return None

    await cache.aset(cache_key, result, timeout=86400)
    return result


def _rtx_response_ok(result: dict[str, Any]) -> bool:
    return result["result"]


def _bk_response_ok(result: dict[str, Any]) -> bool:
    return result["code"] == 0


def _make_user_info(
    result: dict[str, Any] | None, response_ok_checker: ResponseOkChecker, user_info_class: type[TUserInfo]
) -> TUserInfo | None:
    if result and response_ok_checker(result):
        return user_info_class(**result["data"])
    return None
