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
import base64
from typing import Union

from cryptography.hazmat.primitives.ciphers import Cipher

from blue_krill.encoding import force_bytes, force_text


def legacy_decrypt(text: Union[bytes, str], legacy_secret_key: Union[bytes, str]) -> str:
    """解密数据（仅为兼容旧版本，请不要使用）

    :param text: 待解密数据
    :param legacy_secret_key: 用于解密的 secret key
    """
    raw_data = base64.b64decode(text)
    decryptor = _get_cipher(force_bytes(legacy_secret_key)).decryptor()
    result = decryptor.update(raw_data) + decryptor.finalize()
    return force_text(result).strip()


def legacy_encrypt(text: Union[bytes, str], legacy_secret_key: Union[bytes, str]) -> str:
    """加密数据（仅为兼容旧版本，请不要使用）

    :param text: 待加密数据
    :param legacy_secret_key: 用于加密的 secret key
    """
    # Append blank space to extend text in order to make it's length match DES3 block-size(8)
    bytes_text = force_bytes(text)
    if len(bytes_text) % 8 != 0:
        bytes_text += (8 - len(bytes_text) % 8) * b' '

    encryptor = _get_cipher(force_bytes(legacy_secret_key)).encryptor()
    result = encryptor.update(bytes_text) + encryptor.finalize()
    return force_text(base64.b64encode(result))


def _get_cipher(key: bytes) -> Cipher:
    """获取 DES3 Cipher 对象"""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    algorithm = algorithms.TripleDES(key)
    cipher = Cipher(algorithm, modes.CBC(key[:8]), backend=default_backend())
    return cipher
