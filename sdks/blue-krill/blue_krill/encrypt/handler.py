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
from typing import ClassVar, Dict, Optional

from bkcrypto import constants
from bkcrypto.contrib.django.ciphers import get_symmetric_cipher
from bkcrypto.symmetric.options import SM4SymmetricOptions
from cryptography.fernet import Fernet

from blue_krill.encoding import force_bytes, force_text
from blue_krill.encrypt.utils import get_default_encrypt_cipher_type, get_default_secret_key


class _Header:
    def __init__(self, header: str):
        self.header = header

    def add_header(self, text: str):
        return self.header + text

    def strip_header(self, text: str):
        # 兼容无 header 加密串
        if not self.contain_header(text):
            return text
        return text[len(self.header):]

    def contain_header(self, text: str) -> bool:
        return text.startswith(self.header)


class EncryptHandler:
    cipher_classes: ClassVar[Dict] = {}

    def __init__(self, encrypt_cipher_type: Optional[str] = None, secret_key: Optional[bytes] = None):
        self._encrypt_cipher_type = encrypt_cipher_type
        self.secret_key = secret_key or get_default_secret_key()

    @property
    def encrypt_cipher_type(self):
        return self._encrypt_cipher_type or get_default_encrypt_cipher_type()

    def encrypt(self, text: str) -> str:
        """根据指定加密算法，加密字段"""
        # 已加密则不处理
        for _, cls in self.cipher_classes.items():
            if cls.header.contain_header(text):
                return text

        # 根据加密类型配置选择不同的加密算法
        try:
            cipher_class = self.cipher_classes[self.encrypt_cipher_type]
        except KeyError:
            raise ValueError(f"Invalid cipher type: {self.encrypt_cipher_type}")
        else:
            cipher = cipher_class(self.secret_key)
            return cipher.encrypt(text)

    def decrypt(self, encrypted: str) -> str:
        """根据 header 解密"""
        for _, cls in self.cipher_classes.items():
            if cls.header.contain_header(encrypted):
                cipher = cls(self.secret_key)
                return cipher.decrypt(encrypted)
        # 若不包含头则直接返回
        return encrypted


def register_cipher(cls):
    EncryptHandler.cipher_classes[cls.__name__] = cls


@register_cipher
class FernetCipher:
    header = _Header("bkcrypt$")

    def __init__(self, secret_key: Optional[bytes] = None):
        self.secret_key = secret_key or get_default_secret_key()
        self.cipher = Fernet(self.secret_key)

    def encrypt(self, text: str) -> str:
        b_text = force_bytes(text)
        return self.header.add_header(force_text(self.cipher.encrypt(b_text)))

    def decrypt(self, encrypted: str) -> str:
        encrypted = self.header.strip_header(encrypted)

        b_encrypted = force_bytes(encrypted)
        return force_text(self.cipher.decrypt(b_encrypted))


@register_cipher
class SM4CTR:
    header = _Header("sm4ctr$")

    def __init__(self, secret_key: Optional[bytes] = None):
        self.secret_key = secret_key or get_default_secret_key()
        self.cipher = get_symmetric_cipher(
            common={"key": self.secret_key},
            cipher_type=constants.SymmetricCipherType.SM4.value,
            cipher_options={
                constants.SymmetricCipherType.SM4.value: SM4SymmetricOptions(mode=constants.SymmetricMode.CTR)
            },
        )

    def encrypt(self, text: str) -> str:
        return self.header.add_header((self.cipher.encrypt(text)))

    def decrypt(self, encrypted: str) -> str:
        encrypted = self.header.strip_header(encrypted)

        return self.cipher.decrypt(encrypted)
