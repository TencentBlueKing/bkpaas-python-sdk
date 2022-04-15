# -*- coding: utf-8 -*-
from unittest import mock

from bkpaas_auth import get_user_by_user_id
from django.conf import settings
from tests.utils import mock_json_response


def test_get_user_by_user_id(get_rtx_user_info_response):
    with mock.patch('requests.Session.request') as mocked_request:
        mocked_request.return_value = mock_json_response(get_rtx_user_info_response)

        user = get_user_by_user_id(settings.USER_ID, username_only=True)
        assert user.username == settings.USER_NAME
        assert not user.nickname

        user = get_user_by_user_id(settings.USER_ID, username_only=False)
        assert user.username == settings.USER_NAME
        assert user.nickname == settings.USER_NICKNAME
