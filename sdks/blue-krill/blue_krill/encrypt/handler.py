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
from cryptography.fernet import Fernet

from blue_krill.encoding import force_bytes, force_text
from blue_krill.encrypt.utils import get_default_secret_key


class EncryptHandler:
    def __init__(self, secret_key=get_default_secret_key()):
        self.secret_key = secret_key
        self.f = Fernet(self.secret_key)

    def encrypt(self, text: str) -> str:
        if self.Header.contain_header(text):
            return text

        text = force_bytes(text)
        return self.Header.add_header(force_text(self.f.encrypt(text)))

    def decrypt(self, encrypted: str) -> str:
        encrypted = self.Header.strip_header(encrypted)

        encrypted = force_bytes(encrypted)
        return force_text(self.f.decrypt(encrypted))

    class Header:
        HEADER = "bkcrypt$"

        @classmethod
        def add_header(cls, text: str):
            return cls.HEADER + text

        @classmethod
        def strip_header(cls, text: str):
            # 兼容无 header 加密串
            if not cls.contain_header(text):
                return text

            return text[len(cls.HEADER) :]

        @classmethod
        def contain_header(cls, text: str) -> bool:
            return text.startswith(cls.HEADER)
