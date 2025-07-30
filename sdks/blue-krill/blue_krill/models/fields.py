# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

from typing import Optional

from django.db import models

from blue_krill.encrypt.handler import EncryptHandler


class _EncryptedString(str):
    """A string that is encrypted, this type is used to distinguish between normal
    strings and encrypted ones."""


class EncryptField(models.TextField):
    """a field which will be encrypted via cryptography/fernet"""

    description = "a field which will be encrypted"

    def __init__(self, encrypt_cipher_type: Optional[str] = None, secret_key: Optional[bytes] = None, *args, **kwargs):
        super(EncryptField, self).__init__(*args, **kwargs)
        self.handler = EncryptHandler(encrypt_cipher_type=encrypt_cipher_type, secret_key=secret_key)

    def get_prep_value(self, value):
        if value is None:
            return value
        # 如果值已经是 _EncryptedString 实例，则直接返回，避免重复触发加密逻辑
        if isinstance(value, _EncryptedString):
            return value
        return _EncryptedString(self.handler.encrypt(value))

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value)

    def from_db_value(self, value, expression, connection, context=None):
        if value is None:
            return value
        return self.handler.decrypt(value)
