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
from tempfile import SpooledTemporaryFile

import pytest
from moto import mock_s3

from blue_krill.contextlib import nullcontext as does_not_raise
from blue_krill.storages.blobstore.exceptions import ObjectAlreadyExists
from blue_krill.storages.blobstore.s3 import S3Store
from tests.utils import generate_random_string


@pytest.fixture
def store():
    with mock_s3():
        store = S3Store(
            bucket="dummy-bucket",
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
            signature_version="s3v4",
            endpoint_url=None,
            region_name='us-east-1',
        )
        store.get_client().create_bucket(Bucket=store.bucket)
        yield store


@pytest.fixture
def key():
    return generate_random_string()


class TestS3Store:
    def test_upload(self, store, mktemp, key):
        expected = generate_random_string()
        store.upload_file(filepath=mktemp(expected), key=key)
        with open(store.download_file(key=key, filepath=mktemp()), mode="r") as fh:
            assert fh.read() == expected

    @pytest.mark.parametrize(
        "first, second, allow_overwrite, ctx, expected",
        [
            ("first", "second", True, does_not_raise(), "second"),
            ("first", "second", False, pytest.raises(ObjectAlreadyExists), "first"),
        ],
    )
    def test_upload_duplicated(self, store, mktemp, key, first, second, allow_overwrite, ctx, expected):
        store.upload_file(filepath=mktemp(first), key=key)
        with ctx:
            store.upload_file(filepath=mktemp(second), key=key, allow_overwrite=allow_overwrite)

        with open(store.download_file(key=key, filepath=mktemp()), mode="r") as fh:
            assert fh.read() == expected

    def test_generate_presigned_url(self, store, mktemp, key):
        expected = generate_random_string()
        store.upload_file(filepath=mktemp(expected), key=key)
        url = store.generate_presigned_url(key, expires_in=3600)
        assert url

    def test_download_file(self, mktemp, key, store):
        content = generate_random_string()
        store.upload_file(filepath=mktemp(content), key=key)

        filepath = mktemp()
        store.download_file(key=key, filepath=filepath)
        with open(filepath, mode="rb") as fh:
            assert content == fh.read().decode()

    def test_download_fileobj(self, mktemp, key, store):
        content = generate_random_string()
        store.upload_file(filepath=mktemp(content), key=key)
        fh = SpooledTemporaryFile()
        store.download_fileobj(key=key, fh=fh)

        fh.seek(0)
        assert fh.read().decode() == content

    def test_delete_file(self, mktemp, key, store):
        content = generate_random_string()
        store.upload_file(filepath=mktemp(content), key=key)

        assert store.delete_file(key)
        with pytest.raises(Exception) as err:
            store.download_fileobj(key=key, fh=SpooledTemporaryFile())

        assert err.value.response["Error"]["Code"] == "NoSuchKey"

    def test_delete_file_not_exist(self, key, store):
        assert store.delete_file(key)
