# -*- coding: utf-8 -*-
__version__ = "2.0.2"


def get_user_by_user_id(user_id: str, username_only: bool = True):
    """Get a user object from given user_id"""
    from bkpaas_auth.core.constants import ProviderType
    from bkpaas_auth.core.encoder import user_id_encoder
    from bkpaas_auth.core.services import get_bk_user_info, get_rtx_user_info
    from bkpaas_auth.models import User

    provider_type, username = user_id_encoder.decode(user_id)
    user = User(token=None, provider_type=ProviderType(provider_type), username=username)
    if username_only:
        return user

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
