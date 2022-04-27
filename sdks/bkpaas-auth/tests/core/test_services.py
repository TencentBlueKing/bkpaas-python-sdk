# -*- coding: utf-8 -*-
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured

from bkpaas_auth.core.services import _get_app_credentials, conf


class TestGetRTXUserInfoCredentails:
    def test_when_provided(self, settings):
        with mock.patch.multiple(conf, TOKEN_APP_CODE='foo', TOKEN_SECRET_KEY='bar'):
            assert _get_app_credentials() == {'bk_app_code': 'foo', 'bk_app_secret': 'bar'}

    def test_not_provided(self, settings):
        with pytest.raises(ImproperlyConfigured):
            with mock.patch.multiple(
                conf,
                TOKEN_APP_CODE=None,
                TOKEN_SECRET_KEY=None,
            ):
                _get_app_credentials()
