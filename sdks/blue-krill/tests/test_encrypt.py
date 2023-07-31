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

from blue_krill.encrypt.handler import EncryptHandler
from blue_krill.encrypt.legacy import legacy_decrypt, legacy_encrypt


class TestEncrypt:
    def test_encrypt(self):
        encrypt_handler = EncryptHandler(encrypt_cipher_type='FernetCipher', secret_key=Fernet.generate_key())
        encrypted = encrypt_handler.encrypt('foo')
        assert encrypt_handler.decrypt(encrypted) == 'foo'

    def test_sm4cipher_encrypt(self):
        encrypt_handler = EncryptHandler(encrypt_cipher_type='SM4Cipher', secret_key=Fernet.generate_key())
        encrypted = encrypt_handler.encrypt('foo')
        assert encrypt_handler.decrypt(encrypted) == 'foo'

    def test_mixcipher_encrypt(self):
        secret_key = Fernet.generate_key()
        encrypt_handler = EncryptHandler(encrypt_cipher_type='FernetCipher', secret_key=secret_key)
        decrypt_handler = EncryptHandler(encrypt_cipher_type='SM4Cipher', secret_key=secret_key)
        encrypted = encrypt_handler.encrypt('foo')
        decrypted = decrypt_handler.decrypt(encrypted)
        assert decrypted == 'foo'

    def test_mixcipher_encrypt1(self):
        secret_key = Fernet.generate_key()
        decrypt_handler = EncryptHandler(encrypt_cipher_type='FernetCipher', secret_key=secret_key)
        encrypt_handler = EncryptHandler(encrypt_cipher_type='SM4Cipher', secret_key=secret_key)
        encrypted = encrypt_handler.encrypt('foo')
        decrypted = decrypt_handler.decrypt(encrypted)
        assert decrypted == 'foo'


class TestEncryptFromDjangoSetting:
    def test_encrypt(self):
        encrypt_handler = EncryptHandler()
        encrypted = encrypt_handler.encrypt('foo')
        assert encrypt_handler.decrypt(encrypted) == 'foo'

    def test_sm4cipher_encrypt(self):
        encrypt_handler = EncryptHandler()
        encrypted = encrypt_handler.encrypt('foo')
        assert encrypt_handler.decrypt(encrypted) == 'foo'

    def test_mixcipher_encrypt(self):
        encrypt_handler = EncryptHandler()
        decrypt_handler = EncryptHandler()
        encrypted = encrypt_handler.encrypt('foo')
        decrypted = decrypt_handler.decrypt(encrypted)
        assert decrypted == 'foo'

    def test_mixcipher_encrypt1(self):
        decrypt_handler = EncryptHandler()
        encrypt_handler = EncryptHandler()
        encrypted = encrypt_handler.encrypt('foo')
        decrypted = decrypt_handler.decrypt(encrypted)
        assert decrypted == 'foo'


def test_decrypt_legacy():
    encrypted_s = '40Ot6vrbuGI='
    assert legacy_decrypt(encrypted_s, 'a' * 24) == 'foo'


def test_legacy_encrypt():
    assert legacy_encrypt('foo', 'a' * 24) == '40Ot6vrbuGI='


if __name__ == "__main__":
    unittest.main()
