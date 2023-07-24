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
from django.db import models

from blue_krill.encrypt.handler import EncryptHandler, get_encrypt_handler
from blue_krill.encrypt.utils import get_default_secret_key


class EncryptField(models.TextField):
    """a field which will be encrypted via cryptography/fernet"""

    description = "a field which will be encrypted"

    def __init__(self, secret_key: bytes = get_default_secret_key(), *args, **kwargs):
        super(EncryptField, self).__init__(*args, **kwargs)
        # 通过 django setting 配置不同的加密算法 handler，handler 封装了不同的加密算法
        self.handler = get_encrypt_handler()
        # 处理存量数据，暂时只支持国际加密(fernet)->国密算法
        self.legacy_handler = EncryptHandler(secret_key=secret_key)

    # 加密都以配置的算法进行加密
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.handler.encrypt(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value)

    # 解密根据加密头判断使用的算法
    def from_db_value(self, value, expression, connection, context=None):
        if value is None:
            return value
        # 根据加密头，选择不同的加密算法进行解密。
        if self.handler.Header.contain_header(value):
            return self.handler.decrypt(value)
        elif self.legacy_handler.Header.contain_header(value):
            return self.legacy_handler.decrypt(value)
        return value
