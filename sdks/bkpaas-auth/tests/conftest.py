# -*- coding: utf-8 -*-
import logging
import sys

import pytest


def setup_root_logger(level):
    """Set up the root logger, make it to write messages to stdout"""
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        SECRET_KEY='not very secret in tests',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
            },
        ],
        USE_TZ=True,
        TIME_ZONE='Asia/Shanghai',
        MIDDLEWARE=[],
        MIDDLEWARE_CLASSES=[],
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'tests',
        ),
        # bkauth settings
        BKAUTH_BACKEND_TYPE='bk_token',
        BKAUTH_TOKEN_APP_CODE='mock_app_code',
        BKAUTH_TOKEN_SECRET_KEY='mock_app_key',
        BKAUTH_TOKEN_GRANT_ENDPOINT='',
        USER_ID='0221dbef87cd',
        USER_NAME='user1',
        USER_NICKNAME='user1中文名',
        AUTHENTICATION_BACKENDS=["bkpaas_auth.backends.UniversalAuthBackend"],
    )

    try:
        import django

        django.setup()
    except AttributeError:
        pass

    from bkpaas_auth.monkey import patch_middleware_get_user

    patch_middleware_get_user()

    setup_root_logger(logging.DEBUG)


@pytest.fixture
def get_rtx_user_info_response(settings):
    return {
        "message": "",
        "code": 0,
        "data": {
            "bk_username": settings.USER_NAME,
            "LoginName": settings.USER_NAME,
            "ChineseName": settings.USER_NICKNAME,
            "avatar_url": "",
        },
        "result": True,
        "request_id": "ed3c8f75-d956-4dcd-b5d0-7bcd6c2e386a",
    }
