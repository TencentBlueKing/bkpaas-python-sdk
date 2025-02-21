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


from unittest import mock

import pytest
from django.db import transaction

from blue_krill.async_utils.django_utils import apply_async_on_commit, delay_on_commit


@pytest.fixture
def fake_task():
    return mock.MagicMock()


class TestApplyAsyncOnCommit:
    def test_not_in_atomic_block(self, transactional_db, fake_task):
        apply_async_on_commit(fake_task, args=(1, 2), countdown=1)

        fake_task.apply_async.assert_called_once_with(
            args=(1, 2),
            countdown=1,
            ignore_result=True,
        )

    def test_in_atomic_block(self, transactional_db, fake_task):
        with transaction.atomic():
            apply_async_on_commit(fake_task, args=(1, 2), countdown=1)
            fake_task.apply_async.assert_not_called()

        fake_task.apply_async.assert_called_once_with(
            args=(1, 2),
            countdown=1,
            ignore_result=True,
        )

    def test_on_rollback(self, transactional_db, fake_task):
        def _broken_atomic_commit():
            with transaction.atomic():
                apply_async_on_commit(fake_task, args=(1, 2), countdown=1)
                raise ValueError("broken commit")

        with pytest.raises(ValueError, match="broken commit"):
            _broken_atomic_commit()

        fake_task.apply_async.assert_not_called()


class TestDelayOnCommit:
    def test_start_argument(self, transactional_db, fake_task):
        delay_on_commit(fake_task, "arg1", "arg2", countdown=1)

        fake_task.apply_async.assert_called_once_with(
            args=("arg1", "arg2"),
            kwargs={"countdown": 1},
            ignore_result=True,
        )
