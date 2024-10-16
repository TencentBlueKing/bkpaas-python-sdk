# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, fields

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed


def get_settings(name, prefix='BKAUTH_', raise_if_missing=False, default=None):
    """Get a settings value, first in django settings, then find in ConfFixture

    :param str prefix: prefix string using by key in django settings
    :param bool raise_if_missing: raise exception if settings was not set
    """

    def factory():
        name_in_settings = prefix + name
        value = getattr(settings, name_in_settings, default)
        if raise_if_missing and value is None:
            raise ImproperlyConfigured('You must set {} in order to use bkpaas_auth'.format(name_in_settings))
        return value

    return factory


@dataclass
class Settings:

    # 用户登录态认证类型，如 bk_token
    BACKEND_TYPE: str = field(default_factory=get_settings('BACKEND_TYPE'))
    # 验证用户登录态的 API，如 蓝鲸统一登录校验登录态的 API
    USER_COOKIE_VERIFY_URL: str = field(default_factory=get_settings('USER_COOKIE_VERIFY_URL'))

    # 获取用户详情的 API，如中文名、邮箱等，且必须提供应用鉴权信息
    TOKEN_USER_INFO_ENDPOINT: str = field(default_factory=get_settings('TOKEN_USER_INFO_ENDPOINT'))
    TOKEN_APP_CODE: str = field(default_factory=get_settings('TOKEN_APP_CODE'))
    TOKEN_SECRET_KEY: str = field(default_factory=get_settings('TOKEN_SECRET_KEY'))

    LOGIN_TOKEN_EXPIRE_IN: int = field(default_factory=get_settings('LOGIN_TOKEN_EXPIRE_IN', default=24 * 60 * 60))
    SESSION_TIMEOUT: int = field(default_factory=get_settings('SESSION_TIMEOUT', default=5 * 60))

    # 请求第三方 API 设置
    REQUESTS_VERIFY: bool = field(default_factory=get_settings('REQUESTS_VERIFY', default=False))
    REQUESTS_CERT: str = field(default_factory=get_settings('REQUESTS_CERT'))

    # Test data, optional
    USE_MOCKED_USER_INFO: bool = field(default_factory=get_settings('USE_MOCKED_USER_INFO', default=False))
    MOCKED_USER_NAME: str = field(default_factory=get_settings('MOCKED_USER_NAME', default=''))

    def reload(self):
        for f in fields(self):
            setattr(self, f.name, f.default_factory())  # type: ignore


bkauth_settings = Settings()


def reload_settings(*args, **kwargs):
    setting: str = kwargs['setting']
    if setting.startswith("BKAUTH_"):
        bkauth_settings.reload()


setting_changed.connect(reload_settings)
