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
from typing import Any


class RequestError(Exception):
    """服务请求异常"""

    def __init__(self, message: str, code: str = "400", response: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.response = response

    def __str__(self):
        return self.message


class ObjectAlreadyExists(RequestError):
    """该对象已存在."""


class DownloadFailedError(Exception):
    """文件下载失败"""

    def __init__(self, key: str, dest: str):
        """
        :param str key: The name of the key to download from.
        :param str dest: The path to the file to download to.
        """
        super().__init__(key, dest)
        self.key = key
        self.dest = dest


class UploadFailedError(Exception):
    """文件上传失败"""

    def __init__(self, key: str, src: str):
        """
        :param str key: The name of the key to upload to.
        :param str src: The path to the file to upload.
        """
        super().__init__(key, src)
        self.key = key
        self.src = src
