# -*- coding: utf-8 -*-
__version__ = "3.1.0"


def get_user_by_user_id(user_id: str, username_only: bool = True):
    """Get a user object from given user_id"""
    from bkpaas_auth.conf import bkauth_settings as conf
    from bkpaas_auth.core.constants import ProviderType
    from bkpaas_auth.core.encoder import user_id_encoder
    from bkpaas_auth.core.services import get_bk_user_info, get_rtx_user_info
    from bkpaas_auth.models import User

    provider_type, username = user_id_encoder.decode(user_id)
    user = User(token=None, provider_type=ProviderType(provider_type), username=username)

    if username_only:
        return user

    # 多租户模式下, 暂时没有根据用户名获取用户详细信息的接口
    if conf.ENABLE_MULTI_TENANT_MODE:
        raise ValueError('Multi-tenant mode only return username, please set username_only=True')

    # Request third party service to get info other than username
    if provider_type == ProviderType.RTX:
        user_info = get_rtx_user_info(username)
        user_info.provide(user)
        return user
    elif provider_type == ProviderType.BK:
        user_info = get_bk_user_info(username)
        user_info.provide(user)
        return user
    else:
        raise ValueError('ProviderType is not supported yet!')
