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
from typing import Tuple, Union

import requests
from bkpaas_auth.conf import bkauth_settings

logger = logging.getLogger(__name__)

request_adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)


def get_requests_session():
    """Return an empty requests session, use the function to reuse HTTP connections"""
    session = requests.session()
    session.mount("http://", request_adapter)
    session.mount("https://", request_adapter)
    session.verify = bkauth_settings.REQUESTS_VERIFY
    session.cert = bkauth_settings.REQUESTS_CERT
    return session


def _http_request(method: str, url: str, **kwargs) -> Tuple[bool, Union[None, dict, list]]:
    session = get_requests_session()
    try:
        resp = session.request(method, url, **kwargs)
    except requests.exceptions.RequestException:
        logger.exception("http request error! method: %s, url: %s, kwargs: %s", method, url, kwargs)
        return False, None

    logger.debug("request method: %s, url: %s, kwargs: %s", method, url, kwargs)

    try:
        return True, resp.json()
    except json.decoder.JSONDecodeError:
        logger.exception(
            "response json error! method: %s, url: %s, kwargs: %s, response.status_code: %s, response.text: %s",
            method,
            url,
            kwargs,
            resp.status_code,
            resp.text,
        )
        return False, None


def http_get(url: str, **kwargs) -> Tuple[bool, Union[None, dict, list]]:
    return _http_request(method="GET", url=url, **kwargs)


def http_post(url: str, **kwargs) -> Tuple[bool, Union[None, dict, list]]:
    return _http_request(method="POST", url=url, **kwargs)


def http_put(url: str, **kwargs) -> Tuple[bool, Union[None, dict, list]]:
    return _http_request(method="PUT", url=url, **kwargs)


def http_delete(url: str, **kwargs) -> Tuple[bool, Union[None, dict, list]]:
    return _http_request(method="DELETE", url=url, **kwargs)
