# -*- coding: utf-8 -*-
from enum import IntEnum


class ProviderType(IntEnum):
    UIN = 1
    RTX = 2
    BK = 3
    DATABASE = 9

    def get_id_prefix(self):
        return '{0:02d}'.format(self.value)


# 蓝鲸统一登录约定的错误码, 表示用户认证成功，但用户无应用访问权限
ACCESS_PERMISSION_DENIED_CODE = 1302403
