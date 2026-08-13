# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from django.contrib.auth import models
from django.db import models as db_models

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.encoder import user_id_encoder

if TYPE_CHECKING:
    from bkpaas_auth.core.token import LoginToken


class AbstractUserWithProvider(models.AbstractBaseUser, models.AnonymousUser):
    """Basic user with provider type"""

    bkpaas_user_id = db_models.CharField(primary_key=True, max_length=255)
    USERNAME_FIELD = "bkpaas_user_id"
    USERINFO_FIELDS: ClassVar[tuple[str, ...]] = (
        "display_name",
        "tenant_id",
        "time_zone",
        "nickname",
        "chinese_name",
        "avatar_url",
        "email",
        "phone",
    )

    provider_type: ProviderType | None
    username: str | None
    display_name: str | None
    tenant_id: str | None
    time_zone: str | None
    nickname: str | None
    chinese_name: str | None
    avatar_url: str | None
    email: str | None
    phone: str | None

    def __init__(self, provider_type: ProviderType | int | None, username: str | None) -> None:
        if not provider_type:
            self.bkpaas_user_id = "-1"
        elif provider_type not in ProviderType:
            raise ValueError("Invalid provider_type given!")
        elif not username:
            # bkpaas_user_id 由 provider_type 与 username 编码而来，空 username 会让不同用户
            # 编码出同一个 id（仅剩 provider 前缀），而该字段是主键，因此必须显式拒绝。
            raise ValueError("username is required when provider_type is given!")
        else:
            self.bkpaas_user_id = user_id_encoder.encode(provider_type, username)

        self.provider_type = ProviderType(provider_type) if provider_type else None
        self.username = username
        self.password = None
        # Set user info fields to default value: None
        self.update_user_info({}, overwrite_all=True)

    def update_user_info(self, info_dict: dict[str, Any], overwrite_all: bool = False) -> None:
        """Update current user info by dict

        :param overwrite_all: if True, will set emitted field to None if that field is not
            provided by info_dict
        """
        for field in self.USERINFO_FIELDS:
            try:
                value = info_dict[field]
                setattr(self, field, value)
            except KeyError:
                if overwrite_all:
                    setattr(self, field, None)

    def save(self, *args: Any, **kwargs: Any) -> None:
        pass

    def delete(self, *args: Any, **kwargs: Any) -> None:
        pass

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return not (self.is_authenticated)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, models.AnonymousUser):
            return self.is_anonymous
        return super().__eq__(other)

    class Meta:
        abstract = True
        app_label = "bkpaas_auth"


class BasicUser(AbstractUserWithProvider):
    """A basic user object with no extra stuffs"""


class User(AbstractUserWithProvider):
    """Blueking User Model provided by external user systems: Wechat Work or Uin"""

    token: LoginToken | None

    def __init__(
        self,
        token: LoginToken | None = None,
        provider_type: ProviderType | int | None = None,
        username: str | None = None,
        **info_fields: Any,
    ) -> None:
        super().__init__(provider_type, username)

        self.update_user_info(info_fields, overwrite_all=True)
        # Use chinesename as nickname
        if not self.nickname and self.chinese_name:
            self.nickname = self.chinese_name
        self.token = token

    @property
    def is_authenticated(self) -> bool:
        # If self.token has expired, user is considered to be expired too
        # This will force user to re-login again.
        return bool(self.token and not self.token.expired())

    @property
    def is_anonymous(self) -> bool:
        return not self.is_authenticated


class DatabaseUser(AbstractUserWithProvider):
    """Blueking User Model provided by external database"""

    provider_type = ProviderType.DATABASE

    @classmethod
    def from_db_obj(cls, user: Any) -> DatabaseUser:
        obj = cls(cls.provider_type, username=user.username)
        obj._db_object = user
        return obj

    class Meta:
        app_label = "bkpaas_auth"
