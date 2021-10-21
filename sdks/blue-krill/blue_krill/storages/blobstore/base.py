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
from os import PathLike
from typing import Any, BinaryIO, ClassVar

from blue_krill.data_types.enum import EnumField, StructuredEnum


class SignatureType(str, StructuredEnum):
    DOWNLOAD = EnumField("DOWNLOAD", label="下载")
    UPLOAD = EnumField("UPLOAD", label="上传")


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


class BlobStore:
    """BlobStore Protocol, should be implemented by subclass."""

    STORE_TYPE: ClassVar[str]

    def __init__(self, bucket: str):
        self.bucket = bucket

    def get_client(self):
        raise NotImplementedError

    def upload_file(self, filepath: PathLike, key: str, allow_overwrite: bool = True, **kwargs):
        """Upload package to server

        :param PathLike filepath: The path to the file to upload.
        :param str key: key to store the package.
        :param bool allow_overwrite: whether to overwrite the original file
        :raise BlobAlreadyExists: if the key already exists.
        """
        raise NotImplementedError

    def upload_fileobj(self, fh: BinaryIO, key: str, allow_overwrite: bool = True, **kwargs):
        """Upload package to server

        :param BinaryIO fh: A file-like object to upload. At a minimum, it must
                            implement the `read` method, and must return bytes.
        :param str key: The name of the key to upload to.
        :param bool allow_overwrite: whether to overwrite the original file
        :raise BlobAlreadyExists: if the key already exists.
        """
        raise NotImplementedError

    def download_file(self, key: str, filepath: PathLike, *args, **kwargs) -> PathLike:
        """Download file to filepath
        :param str key: The name of the key to download from.
        :param PathLike filepath: The path to the file to download to.
        :return path to download.
        """
        raise NotImplementedError

    def download_fileobj(self, key: str, fh: BinaryIO, *args, **kwargs):
        """Download file to fh
        :param str key: The name of the key to download from.
        :param BinaryIO fh: The fileobj to the file to download to.
        """
        raise NotImplementedError

    def delete_file(self, key: str, *args, **kwargs):
        """Delete file in filepath

        :param str key: The name of the key to delete.
        """
        raise NotImplementedError

    def get_file_metadata(self, key: str):
        """Get file's metadata
        :param str key: The name of the key to read.
        """
        raise NotImplementedError

    def generate_presigned_url(
        self, key: str, expires_in: int, signature_type: SignatureType = SignatureType.DOWNLOAD, *args, **kwargs
    ) -> str:
        """Generate pre-signed url to share blob in store.

        :param str key: key storing the package to be downloaded.
        :param int expires_in: when will the url expire.
        :param SignatureType signature_type: the permision for the presigned url.
        """
        raise NotImplementedError
