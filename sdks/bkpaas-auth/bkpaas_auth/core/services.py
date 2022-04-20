# -*- coding: utf-8 -*-
import logging
from typing import Dict

from bkpaas_auth.conf import bkauth_settings as conf
from bkpaas_auth.core.exceptions import ServiceError
from bkpaas_auth.core.http import http_get
from bkpaas_auth.core.user_info import BkUserInfo, RtxUserInfo
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def _get_app_credentials() -> Dict[str, str]:
    """Get app credentials to verify app, which is required for requesting user info API"""
    if conf.TOKEN_APP_CODE and conf.TOKEN_SECRET_KEY:
        return {'bk_app_code': conf.TOKEN_APP_CODE, 'bk_app_secret': conf.TOKEN_SECRET_KEY}
    raise ImproperlyConfigured("BKAUTH_TOKEN_APP_CODE and BKAUTH_TOKEN_SECRET_KEY not set")


def _get_and_cache_user_info(cache_key, user_params, response_ok_checker):
    """Get user info from cache, or fetch from api and cache

    :param dict user_params: username param key to username map, it may be different in different systems
    :param callable response_ok_checker: determine get user is successful
    """
    try:
        cached_result = cache.get(cache_key)
    except Exception as e:
        # Cache is not usable due to some reason including different pickle protocols
        # between different Python versions.
        logger.warning(f"unable to get user info from cache: {e}")
        cached_result = None

    if cached_result:
        return cached_result

    params = dict(user_params, **_get_app_credentials())
    is_success, result = http_get(conf.TOKEN_USER_INFO_ENDPOINT, params=params)
    if not is_success:
        raise ServiceError('Unable to get user info')

    if not response_ok_checker(result):
        logger.error(
            f'Get user info fail, url: {conf.TOKEN_USER_INFO_ENDPOINT}, params: {params}, response: {result}',
        )
        return

    # 获取用户信息成后才缓存数据
    cache.set(cache_key, result, timeout=86400)

    return result


def get_rtx_user_info(username):
    """Get RTX user info by given RTX username. For better performance, this function
    will try to cache the result for 86400 seconds(1 day).

    :param str username: RTX username
    """

    def response_ok_checker(result):
        return result['result']

    cache_key = f'bkauth::rests::get_rtx_user_info::{username}'
    result = _get_and_cache_user_info(cache_key, {'login_name': username}, response_ok_checker)

    if result and response_ok_checker(result):
        return RtxUserInfo(**result['data'])

    return None


def get_bk_user_info(username):
    """Get BK user info by given BK username. For better performance, this function
    will try to cache the result for 86400 seconds(1 day).

    :param str username: BK username
    """

    def response_ok_checker(result):
        return result['code'] == 0

    cache_key = f'bkauth::rests::get_bk_user_info::{username}'
    result = _get_and_cache_user_info(cache_key, {'bk_username': username}, response_ok_checker)

    if result and response_ok_checker(result):
        return BkUserInfo(**result['data'])

    return None
