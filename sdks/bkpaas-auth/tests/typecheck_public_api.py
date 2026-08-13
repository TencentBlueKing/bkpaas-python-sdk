"""Static checks for the type contracts exposed to package consumers."""

from typing import Any, assert_type

import httpx2
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from bkpaas_auth.backends import APIGatewayAuthBackend
from bkpaas_auth.conf import bkauth_settings
from bkpaas_auth.core.http import JSONValue, resp_to_json
from bkpaas_auth.core.user_info import RtxUserInfo
from bkpaas_auth.models import User
from bkpaas_auth.utils import scrub_data


def check_public_api_types(request: HttpRequest, response: httpx2.Response) -> None:
    """Exercise supported calls so mypy checks them as a package consumer would."""
    backend = APIGatewayAuthBackend()

    assert_type(
        backend.authenticate(request=request, api_name="api", bk_username="v1-user", verified=True),
        User | AnonymousUser,
    )
    assert_type(
        backend.authenticate(request=request, gateway_name="gateway", bk_username="v3-user"),
        User | AnonymousUser,
    )
    assert_type(scrub_data("token=value"), str)
    assert_type(scrub_data({"value": 1}), dict[str, Any])
    assert_type(bkauth_settings.BACKEND_TYPE, str | None)
    assert_type(bkauth_settings.USER_COOKIE_VERIFY_URL, str | None)
    assert_type(bkauth_settings.USER_INFO_APIGW_URL, str | None)
    assert_type(bkauth_settings.TOKEN_USER_INFO_ENDPOINT, str | None)
    assert_type(bkauth_settings.TOKEN_APP_CODE, str | None)
    assert_type(bkauth_settings.TOKEN_SECRET_KEY, str | None)
    assert_type(bkauth_settings.REQUESTS_CERT, str | None)
    assert_type(resp_to_json(response), JSONValue)

    rtx_user_info = RtxUserInfo.parse_json({})
    assert_type(rtx_user_info, RtxUserInfo)
    assert_type(rtx_user_info.email, str)
