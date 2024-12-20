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
from typing import Union

import requests

from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.exceptions import HttpRequestError, ServiceError
from bkpaas_auth.utils import scrub_data

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


def build_req_details_str(method, url, params, data, **kwargs) -> str:
    """Build the request details string for logging purpose."""
    msg = f'{method} {url}'
    if params:
        msg += f', params: {scrub_data(params)}'
    if data:
        msg += f', data: {scrub_data(data)}'
    msg += f', kwargs: {kwargs}'
    return msg


def _http_request(method: str, url: str, **kwargs) -> requests.Response:
    session = get_requests_session()
    params = kwargs.pop("params", None)
    data = kwargs.pop("data", None)

    req_details = build_req_details_str(method, url, params, data, **kwargs)
    logger.debug("Sending HTTP request, req details: %s", req_details)

    try:
        resp = session.request(method, url, params=params, data=data, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.exception("http request error! req details: %s", req_details)
        raise HttpRequestError(f"http request error: {e}")

    return resp


def resp_to_json(resp: requests.Response) -> Union[dict, list]:
    try:
        return resp.json()
    except json.decoder.JSONDecodeError:
        logger.exception(
            "response json error! response.status_code: %s, response.text: %s",
            resp.status_code,
            resp.text,
        )
        raise ServiceError("parse json response error")


def http_get(url: str, **kwargs) -> requests.Response:
    return _http_request(method="GET", url=url, **kwargs)
