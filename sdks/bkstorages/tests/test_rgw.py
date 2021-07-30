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
import datetime
from tempfile import NamedTemporaryFile

import pytest
import six
from bkstorages.backends.rgw import RGWBoto3Storage
from django.core.files import File
from django.core.files.base import ContentFile

from .models import RGWFile

pytestmark = pytest.mark.django_db


def make_content_file(content=None):
    """Make a django ContentFile object"""
    if not content:
        content = "written by pytest"
    content_bytes = six.b(content)
    return ContentFile(content_bytes)


@pytest.fixture
def storage():
    return RGWBoto3Storage()


class TestRGWBoto3Storage:
    def test_save_content_file(self, storage):
        f = make_content_file()
        assert storage.save(u"/test/content_file", f) == "/test/content_file"
        assert storage.save(u"/test/中文名称", f) == u"/test/中文名称"

    def test_save_file(self, storage):
        with NamedTemporaryFile() as fp:
            fp.write(six.b("by_test_save"))
            fp.flush()

            f = File(fp)
            assert storage.save(u"/test/file", f) == "/test/file"

    def test_listdir(self, storage):
        assert len(storage.listdir("/test")[1]) > 0

    def test_delete(self, storage):
        fname = u"/test/to_be_removed"

        storage.save(fname, make_content_file())
        assert storage.exists(fname) is True
        # File should
        storage.delete(fname)
        assert storage.exists(fname) is False

    def test_mtime(self, storage):
        fname = u"/test/content_file"
        storage.save(fname, make_content_file())
        assert (datetime.datetime.now() - storage.modified_time(fname)).total_seconds() < 5

    def test_location(self, storage):
        storage = RGWBoto3Storage(location="/static/")
        storage.save(u"test/content_file", make_content_file())


class TestFileWithStorage:
    @pytest.mark.parametrize("pic_filename", ["tests/flower.png"])
    def test_upload(self, pic_filename):
        f = File(open(pic_filename, "rb"))
        obj = RGWFile(user_id=3074, user_file=f)
        obj.save()

        # Make sure file downloaded is same with origin
        obj = RGWFile.objects.get(pk=obj.id)
        with open(pic_filename, "rb") as fp:
            assert fp.read() == obj.user_file.read()
