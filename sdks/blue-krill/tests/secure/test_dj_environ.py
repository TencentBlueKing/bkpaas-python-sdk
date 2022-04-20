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
from functools import partial

import pytest
from blue_krill.encrypt.utils import encrypt_string
from blue_krill.secure.dj_environ import EncryptedEnviron, SecureEnv
from cryptography.fernet import Fernet


class TestSecureEnv:
    def test_encrypted_value(self, monkeypatch):
        monkeypatch.setenv('DATABASE_URL', encrypt_string('mysql://u:p@localhost/foo'))
        env = SecureEnv()
        assert env.db_url() is not None
        assert env.db_url()['HOST'] == 'localhost'

    def test_plain_value(self, monkeypatch):
        monkeypatch.setenv('DATABASE_URL', 'mysql://u:p@localhost/foo')
        env = SecureEnv()
        with pytest.raises(ValueError):
            env.db_url()

    def test_set_encryption_key(self, monkeypatch):
        monkeypatch.setenv('DATABASE_URL', encrypt_string('mysql://u:p@localhost/foo'))
        env = SecureEnv()
        # Set an invalid secure key
        env.set_secure_key(Fernet.generate_key())
        with pytest.raises(ValueError):
            env.db_url()

    def test_decrypt_function(self, monkeypatch):
        raw = "testing"
        monkeypatch.setenv('ENCRYPT_VALUE', encrypt_string(raw))

        class MySecureEnv(SecureEnv):
            ENVIRON_CLS = partial(EncryptedEnviron, decryptor=lambda value, key: raw)

        env = MySecureEnv()
        assert env.str("ENCRYPT_VALUE") == raw
