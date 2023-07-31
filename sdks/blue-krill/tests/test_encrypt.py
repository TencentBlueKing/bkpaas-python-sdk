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
import unittest

from cryptography.fernet import Fernet
from django.test.utils import override_settings

from blue_krill.encrypt.handler import EncryptHandler
from blue_krill.encrypt.legacy import legacy_decrypt, legacy_encrypt


class TestEncrypt:
    def test_encrypt(self):
        encrypt_handler = EncryptHandler(encrypt_cipher_type='FernetCipher', secret_key=Fernet.generate_key())
        for i in range(10):
            text = random_string(10)
            encrypted = encrypt_handler.encrypt(text)
            assert encrypt_handler.decrypt(encrypted) == text

    def test_sm4cipher_encrypt(self):
        encrypt_handler = EncryptHandler(encrypt_cipher_type='SM4Cipher', secret_key=Fernet.generate_key())
        for i in range(10):
            text = random_string(10)
            encrypted = encrypt_handler.encrypt(text)
            assert encrypt_handler.decrypt(encrypted) == text

    def test_mixcipher_encrypt(self):
        secret_key = Fernet.generate_key()
        encrypt_handler = EncryptHandler(encrypt_cipher_type='FernetCipher', secret_key=secret_key)
        decrypt_handler = EncryptHandler(encrypt_cipher_type='SM4Cipher', secret_key=secret_key)
        for i in range(10):
            text = random_string(10)
            encrypted = encrypt_handler.encrypt(text)
            assert encrypted.startswith("bkcrypt$")
            assert decrypt_handler.decrypt(encrypted) == text

    def test_mixcipher_encrypt1(self):
        secret_key = Fernet.generate_key()
        decrypt_handler = EncryptHandler(encrypt_cipher_type='FernetCipher', secret_key=secret_key)
        encrypt_handler = EncryptHandler(encrypt_cipher_type='SM4Cipher', secret_key=secret_key)
        for i in range(10):
            text = random_string(10)
            encrypted = encrypt_handler.encrypt(text)
            assert encrypted.startswith("sm4$")
            assert decrypt_handler.decrypt(encrypted) == text


class TestEncryptFromDjangoSetting:
    def test_encrypt(self):
        encrypt_handler = EncryptHandler()
        for i in range(10):
            text = random_string(10)
            encrypted = encrypt_handler.encrypt(text)
            assert encrypt_handler.decrypt(encrypted) == text

    def test_sm4cipher_encrypt(self):
        encrypt_handler = EncryptHandler()
        for i in range(10):
            text = random_string(10)
            encrypted = encrypt_handler.encrypt(text)
            assert encrypt_handler.decrypt(encrypted) == text

    def test_mixcipher_encrypt(self):
        key = Fernet.generate_key()
        with override_settings(ENCRYPT_CIPHER_TYPE='FernetCipher', BKKRILL_ENCRYPT_SECRET_KEY=key):
            encrypt_handler = EncryptHandler()
        with override_settings(ENCRYPT_CIPHER_TYPE='SM4Cipher', BKKRILL_ENCRYPT_SECRET_KEY=key):
            decrypt_handler = EncryptHandler()
        for i in range(10):
            text = random_string(10)
            encrypted = encrypt_handler.encrypt(text)
            assert encrypted.startswith("bkcrypt$")
            assert decrypt_handler.decrypt(encrypted) == text

    def test_mixcipher_encrypt1(self):
        key = Fernet.generate_key()
        with override_settings(ENCRYPT_CIPHER_TYPE='SM4Cipher', BKKRILL_ENCRYPT_SECRET_KEY=key):
            encrypt_handler = EncryptHandler()
        with override_settings(ENCRYPT_CIPHER_TYPE='FernetCipher', BKKRILL_ENCRYPT_SECRET_KEY=key):
            decrypt_handler = EncryptHandler()
        for i in range(10):
            text = random_string(10)
            encrypted = encrypt_handler.encrypt(text)
            assert encrypted.startswith("sm4$")
            assert decrypt_handler.decrypt(encrypted) == text


def test_decrypt_legacy():
    encrypted_s = '40Ot6vrbuGI='
    assert legacy_decrypt(encrypted_s, 'a' * 24) == 'foo'


def test_legacy_encrypt():
    assert legacy_encrypt('foo', 'a' * 24) == '40Ot6vrbuGI='


def random_string(length):
    import random
    import string

    # 定义用于生成随机字符串的字符集
    characters = string.ascii_letters + string.digits
    # 生成随机字符串
    random_str = ''.join(random.choice(characters) for i in range(length))
    return random_str


def test_encrypt_legacy():
    """
    测试 legacy 加密
    """


if __name__ == "__main__":
    unittest.main()
