# -*- coding: utf-8 -*-
__version__ = "4.3.0"


def _prepare_user_lookup(user_id, username_only):
    from bkpaas_auth.conf import bkauth_settings as conf  # noqa: PLC0415
    from bkpaas_auth.core.constants import ProviderType  # noqa: PLC0415
    from bkpaas_auth.core.encoder import user_id_encoder  # noqa: PLC0415
    from bkpaas_auth.models import User  # noqa: PLC0415

    provider_type, username = user_id_encoder.decode(user_id)
    provider_type = ProviderType(provider_type)
    user = User(token=None, provider_type=provider_type, username=username)

    if username_only:
        return provider_type, username, user, False

    # 多租户模式下, 暂时没有根据用户名获取用户详细信息的接口
    if conf.ENABLE_MULTI_TENANT_MODE:
        raise ValueError("Multi-tenant mode only return username, please set username_only=True")
    return provider_type, username, user, True


def _provide_user_info(user, user_info):
    user_info.provide(user)
    return user


def get_user_by_user_id(user_id: str, username_only: bool = True):
    """Get a user object from given user_id."""
    from bkpaas_auth.core.constants import ProviderType  # noqa: PLC0415
    from bkpaas_auth.core.services import get_bk_user_info, get_rtx_user_info  # noqa: PLC0415

    provider_type, username, user, should_fetch_user_info = _prepare_user_lookup(user_id, username_only)
    if not should_fetch_user_info:
        return user

    # Request third party service to get info other than username
    if provider_type == ProviderType.RTX:
        user_info = get_rtx_user_info(username)
    elif provider_type == ProviderType.BK:
        user_info = get_bk_user_info(username)
    else:
        raise ValueError("ProviderType is not supported yet!")
    return _provide_user_info(user, user_info)


async def async_get_user_by_user_id(user_id: str, username_only: bool = True):
    """Asynchronously get a user object from a user ID."""
    from bkpaas_auth.core.constants import ProviderType  # noqa: PLC0415
    from bkpaas_auth.core.services import async_get_bk_user_info, async_get_rtx_user_info  # noqa: PLC0415

    provider_type, username, user, should_fetch_user_info = _prepare_user_lookup(user_id, username_only)
    if not should_fetch_user_info:
        return user

    if provider_type == ProviderType.RTX:
        user_info = await async_get_rtx_user_info(username)
    elif provider_type == ProviderType.BK:
        user_info = await async_get_bk_user_info(username)
    else:
        raise ValueError("ProviderType is not supported yet!")
    return _provide_user_info(user, user_info)
