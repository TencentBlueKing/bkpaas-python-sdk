# -*- coding: utf-8 -*-
from typing import Dict

from django.contrib.auth import models
from django.db import models as db_models

from bkpaas_auth.core.constants import ProviderType
from bkpaas_auth.core.encoder import user_id_encoder


class AbstractUserWithProvider(models.AbstractBaseUser, models.AnonymousUser):
    """Basic user with provider type"""

    bkpaas_user_id = db_models.CharField(primary_key=True, max_length=255)
    USERNAME_FIELD = 'bkpaas_user_id'
    USERINFO_FIELDS = ('nickname', 'chinese_name', 'avatar_url', 'email', 'phone')

    def __init__(self, provider_type, username):
        if not provider_type:
            self.bkpaas_user_id = '-1'
        elif provider_type not in ProviderType:
            raise ValueError('Invalid provider_type given!')
        else:
            self.bkpaas_user_id = user_id_encoder.encode(provider_type, username)

        self.provider_type = provider_type
        self.username = username
        self.password = None
        # Set user info fields to default value: None
        self.update_user_info({}, overwrite_all=True)

    def update_user_info(self, info_dict: Dict, overwrite_all=False):
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

    def save(*args, **kwargs):
        pass

    def delete(*args, **kwargs):
        pass

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return not (self.is_authenticated)

    def __eq__(self, other):
        if isinstance(other, models.AnonymousUser):
            return self.is_anonymous
        return super(AbstractUserWithProvider, self).__eq__(other)

    class Meta:
        abstract = True
        app_label = 'bkpaas_auth'


class BasicUser(AbstractUserWithProvider):
    """A basic user object with no extra stuffs"""


class User(AbstractUserWithProvider):
    """Blueking User Model provided by external user systems: Wechat Work or Uin"""

    def __init__(self, token=None, provider_type=None, username=None, **info_fields):
        super().__init__(provider_type, username)

        self.update_user_info(info_fields, overwrite_all=True)
        # Use chinesename as nickname
        if not self.nickname and self.chinese_name:  # type: ignore
            self.nickname = self.chinese_name
        self.token = token

    @property
    def is_authenticated(self):
        # If self.token has expired, user is considered to be expired too
        # This will force user to re-login again.
        return bool(self.token and not self.token.expired())

    @property
    def is_anonymous(self):
        return not self.is_authenticated


class DatabaseUser(AbstractUserWithProvider):
    """Blueking User Model provided by external database"""

    provider_type = ProviderType.DATABASE

    @classmethod
    def from_db_obj(cls, user):
        obj = cls(cls.provider_type, username=user.username)
        obj._db_object = user
        return obj

    class Meta:
        app_label = 'bkpaas_auth'
