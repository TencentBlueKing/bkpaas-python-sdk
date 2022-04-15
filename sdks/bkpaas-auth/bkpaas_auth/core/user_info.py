# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.encoder import user_id_encoder

if TYPE_CHECKING:
    from bkpaas_auth.models import User  # noqa


class UserInfo:
    """Base class for Userinfo"""

    provider_type: ProviderType

    def __init__(self, username):
        self.username = username

    def provide(self, user: 'User'):
        user.provider_type = self.provider_type
        user.username = self.username
        user.bkpaas_user_id = user_id_encoder.encode(self.provider_type, self.username)

        user.update_user_info(self.__dict__)
        return user

    def __eq__(self, other):
        if not isinstance(other, UserInfo):
            return False
        return self.username == other.username


class RtxUserInfo(UserInfo):
    """User info for RTX user"""

    provider_type = ProviderType.RTX
    email_suffix = "@tencent.com"

    def __init__(self, **kwargs):
        super().__init__(kwargs["LoginName"])
        self.nickname = kwargs['ChineseName']
        self.chinese_name = kwargs['ChineseName']
        self.email = f'{self.username}{self.email_suffix}'
        # 用户 API 添加了限制，没有申请特殊权限的情况下无法获取手机信息
        self.phone = kwargs.get('MobilePhoneNumber', '')
        self.avatar_url = ''

    def __eq__(self, other):
        if not isinstance(other, RtxUserInfo):
            return False
        return (self.username, self.nickname, self.chinese_name, self.email, self.phone) == (
            other.username,
            other.nickname,
            other.chinese_name,
            other.email,
            other.phone,
        )


class BkUserInfo(UserInfo):
    """User info for Bk user"""

    provider_type = ProviderType.BK

    def __init__(self, **kwargs):
        # bk_username 用户英文ID
        super().__init__(kwargs["bk_username"])
        # chname 用户中文名
        self.nickname = kwargs['chname']
        self.chinese_name = kwargs['chname']
        self.email = kwargs['email']
        self.phone = kwargs['phone']
        self.avatar_url = ''

    def __eq__(self, other):
        if not isinstance(other, BkUserInfo):
            return False
        return (self.username, self.nickname, self.chinese_name, self.email, self.phone) == (
            other.username,
            other.nickname,
            other.chinese_name,
            other.email,
            other.phone,
        )
