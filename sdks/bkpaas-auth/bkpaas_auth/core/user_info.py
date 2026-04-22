# -*- coding: utf-8 -*-
import json
from typing import TYPE_CHECKING, Any, ClassVar, Tuple

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.encoder import user_id_encoder

if TYPE_CHECKING:
    from bkpaas_auth.models import User  # noqa


class UserInfo:
    """Base class for UserInfo"""

    provider_type: ProviderType
    _json_fields: ClassVar[Tuple[str, ...]] = (
        "provider_type",
        "username",
        "display_name",
        "time_zone",
        "tenant_id",
    )

    def __init__(self, username, **kwargs):
        self.username = username
        self.display_name = kwargs.get("display_name") or username
        self.time_zone = kwargs.get("time_zone")
        self.tenant_id = kwargs.get("tenant_id")

    def provide(self, user: "User"):
        user.provider_type = self.provider_type
        user.username = self.username
        user.bkpaas_user_id = user_id_encoder.encode(self.provider_type, self.username)

        user.update_user_info(self.__dict__)
        return user

    def dump_json(self) -> str:
        payload = {}
        for field in self._json_fields:
            value = getattr(self, field, None)
            if field == "provider_type" and value is not None:
                value = int(value)
            payload[field] = value
        return json.dumps(payload)

    @classmethod
    def parse_json(cls, payload: str | dict[str, Any]) -> "UserInfo":
        data = cls._parse_json_payload(payload)
        user_info = cls.__new__(cls)
        for field in cls._json_fields:
            value = data.get(field)
            if field == "provider_type" and value is not None:
                value = ProviderType(value)
            setattr(user_info, field, value)
        return user_info

    def __eq__(self, other):
        if not isinstance(other, UserInfo):
            return False
        return self.username == other.username

    @staticmethod
    def _parse_json_payload(payload: str | dict[str, Any]) -> dict[str, Any]:
        """Parse the JSON payload to dict."""
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict):
            raise TypeError(f"serialized payload must be dict, got: {type(payload)!r}")
        return payload


class RtxUserInfo(UserInfo):
    """User info for RTX user"""

    provider_type = ProviderType.RTX
    email_suffix = "@tencent.com"

    _json_fields = UserInfo._json_fields + (
        "nickname",
        "chinese_name",
        "email",
        "phone",
        "avatar_url",
    )

    def __init__(self, **kwargs):
        super().__init__(kwargs["LoginName"], **kwargs)
        self.nickname = kwargs["ChineseName"]
        self.chinese_name = kwargs["ChineseName"]
        self.email = f"{self.username}{self.email_suffix}"
        # 用户 API 添加了限制，没有申请特殊权限的情况下无法获取手机信息
        self.phone = kwargs.get("MobilePhoneNumber", "")
        self.avatar_url = ""

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
    _json_fields = UserInfo._json_fields + (
        "nickname",
        "chinese_name",
        "email",
        "phone",
        "avatar_url",
    )

    def __init__(self, **kwargs):
        # bk_username 用户英文ID
        super().__init__(kwargs["bk_username"], **kwargs)
        # chname 用户中文名
        self.nickname = kwargs["chname"]
        self.chinese_name = kwargs["chname"]
        self.email = kwargs["email"]
        self.phone = kwargs["phone"]
        self.avatar_url = ""

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
