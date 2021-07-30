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
import logging
from os import PathLike
from shutil import copyfileobj
from typing import BinaryIO

from blue_krill.storages.blobstore.base import BlobStore, ObjectAlreadyExists, SignatureType

try:
    import boto3
    from botocore.client import Config
    from botocore.exceptions import ClientError
except ImportError as e:
    raise ImportError("Please install boto3=='^1.4.3'") from e


logger = logging.getLogger(__name__)


class S3Store(BlobStore):
    """支持 S3 协议的对象存储服务"""

    STORE_TYPE = "s3"

    def __init__(
        self,
        bucket: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: str,
        region_name: str = 'us-east-1',
        signature_version: str = "s3v4",
        **kwargs,
    ):
        super().__init__(bucket)
        self.signature_version = signature_version
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.region_name = region_name

    def get_client(self, signature_version: str = None):
        return boto3.resource(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url,
            config=Config(
                region_name=self.region_name,
                signature_version=signature_version or self.signature_version,
            ),
        )

    def upload_file(self, filepath: PathLike, key: str, allow_overwrite: bool = True, **kwargs):
        client = self.get_client()
        logger.info("Start uploading package to S3 server...")
        bucket = client.Bucket(self.bucket)
        # 由于 S3 默认的上传行为是覆盖, 因此如果不允许覆盖, 只能先发请求判断文件是否存在, 再进行上传操作.
        if not allow_overwrite:
            self.check_key_exists_in_bucket(client, bucket=self.bucket, key=key)
        bucket.upload_file(str(filepath), key, **kwargs)
        logger.info("Upload finished.")

    def upload_fileobj(self, fh: BinaryIO, key: str, allow_overwrite: bool = True, **kwargs):
        client = self.get_client()
        logger.info("Start uploading package to S3 server...")
        bucket = client.Bucket(self.bucket)
        # 由于 S3 默认的上传行为是覆盖, 因此如果不允许覆盖, 只能先发请求判断文件是否存在, 再进行上传操作.
        if not allow_overwrite:
            self.check_key_exists_in_bucket(client, bucket=self.bucket, key=key)
        bucket.upload_fileobj(fh, key, **kwargs)
        logger.info("Upload finished.")

    def download_file(self, key: str, filepath: PathLike, *args, **kwargs) -> PathLike:
        client = self.get_client()
        bucket = client.Bucket(self.bucket)
        bucket.download_file(key, str(filepath))
        return filepath

    def download_fileobj(self, key: str, fh: BinaryIO, *args, **kwargs):
        client = self.get_client()
        bucket = client.Bucket(self.bucket)
        obj = bucket.Object(key).get()
        copyfileobj(obj["Body"], fh)

    def delete_file(self, key: str, *args, **kwargs):
        client = self.get_client()
        bucket = client.Bucket(self.bucket)
        return bucket.Object(key).delete()

    def get_file_metadata(self, key: str):
        client = self.get_client()
        bucket = client.Bucket(self.bucket)
        obj = bucket.Object(key).get()
        return obj

    def generate_presigned_url(
        self, key: str, expires_in: int, signature_type: SignatureType = SignatureType.DOWNLOAD, *args, **kwargs
    ) -> str:
        # Must set signature_version to s3 instead of s3v4 or the generated presigned url
        # won't work "signature not match" error
        operation_name = {SignatureType.DOWNLOAD: "get_object", SignatureType.UPLOAD: "put_object"}[
            (SignatureType(signature_type))
        ]
        client = self.get_client(signature_version="s3")
        url = client.meta.client.generate_presigned_url(
            operation_name,
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url

    @staticmethod
    def check_key_exists_in_bucket(client, bucket, key):
        try:
            client.Object(bucket, key).load()
            raise ObjectAlreadyExists(f"A source package with the same key[{key}] already exists.", code="Unknown")
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code != "404":
                raise ObjectAlreadyExists(
                    f"A source package with the same key[{key}] already exists.", code=code, response=e.response
                )
