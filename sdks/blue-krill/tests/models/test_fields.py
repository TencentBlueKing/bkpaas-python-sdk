# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import pytest

from blue_krill.models.fields import EncryptField
from tests.models.apps.test_encrypt.models import TestEncryptFieldModel

pytestmark = pytest.mark.django_db


class TestEncryptField:
    @pytest.fixture(
        params=[
            # Test the fields with different ciphers
            "data",
            "data_fernet",
            "data_sm4",
        ]
    )
    def field_name(self, request):
        return request.param

    def test_basic_encryption_decryption(self, field_name):
        test_data = "This is sensitive information"
        obj = TestEncryptFieldModel.objects.create(name="test_object", **{field_name: test_data})

        obj_from_db = TestEncryptFieldModel.objects.get(id=obj.id)
        assert getattr(obj_from_db, field_name) == test_data

    def test_none_value_handling(self, field_name):
        obj = TestEncryptFieldModel.objects.create(name="test_none", **{field_name: None})

        obj_from_db = TestEncryptFieldModel.objects.get(id=obj.id)
        assert getattr(obj_from_db, field_name) is None

    def test_empty_string_handling(self, field_name):
        obj = TestEncryptFieldModel.objects.create(name="test_empty", **{field_name: ""})

        obj_from_db = TestEncryptFieldModel.objects.get(id=obj.id)
        assert getattr(obj_from_db, field_name) == ""

    def test_value_with_encrypt_header(self):
        # Create a value that has the Fernet header but is not a real encrypted value
        test_data = "bkcrypt$this_looks_like_encrypted_but_is_not"
        obj = TestEncryptFieldModel.objects.create(name="test_header_fernet", data_fernet=test_data)

        retrieved_obj = TestEncryptFieldModel.objects.get(id=obj.id)
        assert retrieved_obj.data_fernet == test_data

    def test_data_is_actually_encrypted_in_db(self):
        """Test that data is actually encrypted when stored in database"""
        test_data = "This should be encrypted in DB"

        obj = TestEncryptFieldModel.objects.create(
            name="test_encryption_verification",
            data_fernet=test_data,
            data_sm4=test_data,
        )

        # Query the raw value from database
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT data_fernet, data_sm4 FROM test_encrypt_testencryptfieldmodel WHERE id = %s",
                [obj.id],
            )
            raw_fernet_value, raw_sm4_value = cursor.fetchone()

        assert raw_fernet_value != test_data, "The value in the database should be encrypted"
        assert raw_fernet_value.startswith("bkcrypt$")
        assert raw_sm4_value != test_data, "The value in the database should be encrypted"
        assert raw_sm4_value.startswith("sm4ctr$")

    def test_get_prep_value_no_repeat_encryption(self):
        """Test get_prep_value method with string value"""
        field = EncryptField()
        test_data = "test string"
        # Call get_prep_value for multiple times
        value = field.get_prep_value(test_data)
        value = field.get_prep_value(value)
        value = field.get_prep_value(value)

        assert field.from_db_value(value, None, None, None) == test_data, "Value should not be re-encrypted"
