# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""
import os
from typing import Optional

from cryptography.fernet import InvalidToken
from environ import Env

from blue_krill.encrypt.utils import decrypt_string


class EncryptedEnviron:
    """A wrapper class which reads encrypted values from os.environ

    :param key: if not given, decryptor may use default secret key from settings
    :param decryptor: a callable object that decrypt the value by key
    """

    def __init__(self, environ=None, key: Optional[bytes] = None, decryptor=decrypt_string):
        self.environ = environ or os.environ
        self.key = key
        self.decryptor = decryptor

    def __getitem__(self, key) -> str:
        """Overwrite the default env[var_name] behavior with an extra decryption step

        :raises: ValueError when value was not encrypted by fernet
        """
        _value = self.environ[key]

        try:
            return self.decryptor(_value, key=self.key)
        except InvalidToken:
            raise ValueError(f'Var "{key}" was not encrypted or token is invalid, please use plain text mode instead')


class SecureEnv(Env):
    """Allow to read value from encrypted environment variables"""

    ENVIRON_CLS = EncryptedEnviron

    def set_secure_key(self, key: bytes):
        """Set a different key for decryption"""
        self.ENVIRON = self.ENVIRON_CLS(key=key)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ENVIRON = self.ENVIRON_CLS()
