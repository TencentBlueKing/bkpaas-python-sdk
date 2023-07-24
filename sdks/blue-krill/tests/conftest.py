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
from typing import List

from bkcrypto import constants
from bkcrypto.symmetric.options import AESSymmetricOptions, SM4SymmetricOptions
from cryptography.fernet import Fernet


def pytest_configure():
    from django.conf import settings

    MIDDLEWARE: List = []

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        SECRET_KEY='not very secret in tests',
        TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'APP_DIRS': True}],
        USE_TZ=True,
        TIME_ZONE='Asia/Shanghai',
        MIDDLEWARE=MIDDLEWARE,
        MIDDLEWARE_CLASSES=MIDDLEWARE,
        INSTALLED_APPS=(),
        # Config for testing encrypt related functions
        BKKRILL_ENCRYPT_SECRET_KEY=Fernet.generate_key(),
        BKKRILL_ENCRYPT_HANDLER='NationEncryptHandler',
        BKCRYPTO={
            # 声明项目所使用的非对称加密算法
            "ASYMMETRIC_CIPHER_TYPE": constants.AsymmetricCipherType.SM2.value,
            # 声明项目所使用的对称加密算法
            "SYMMETRIC_CIPHER_TYPE": constants.SymmetricCipherType.SM4.value,
            "SYMMETRIC_CIPHERS": {
                # default - 所配置的对称加密实例，根据项目需要可以配置多个
                "default": {
                    # 可选，用于在 settings 没法直接获取 key 的情况
                    # "get_key_config": "apps.utils.encrypt.key.get_key_config",
                    # 可选，用于 ModelField，加密时携带该前缀入库，解密时分析该前缀并选择相应的解密算法
                    # ⚠️ 前缀和 cipher type 必须一一对应，且不能有前缀匹配关系
                    # "db_prefix_map": {
                    #     SymmetricCipherType.AES.value: "aes_str:::",
                    #     SymmetricCipherType.SM4.value: "sm4_str:::"
                    # },
                    "common": {"key": os.urandom(24)},
                    "cipher_options": {
                        constants.SymmetricCipherType.AES.value: AESSymmetricOptions(
                            key_size=24,
                            iv=os.urandom(16),
                            mode=constants.SymmetricMode.CFB,
                            encryption_metadata_combination_mode=(
                                constants.EncryptionMetadataCombinationMode.STRING_SEP
                            ),
                        ),
                        constants.SymmetricCipherType.SM4.value: SM4SymmetricOptions(mode=constants.SymmetricMode.CTR),
                    },
                },
            },
        },
    )

    try:
        import django

        django.setup()
    except AttributeError:
        pass
