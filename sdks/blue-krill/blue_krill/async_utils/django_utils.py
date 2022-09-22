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
from functools import partial
from typing import Optional

from django.db import transaction

logger = logging.getLogger(__name__)


def apply_async_on_commit(celery_task, using: Optional[str] = None, *args, **kwargs):
    """
    Apply celery task async and always ignore the task result,
    it will trigger the task on transaction commit when it is in a atomic block.
    """

    fn = partial(celery_task.apply_async, ignore_result=True, *args, **kwargs)

    connection = transaction.get_connection(using)
    if connection.in_atomic_block:
        logger.debug("trigger task %s on transaction commit", celery_task.name)
        transaction.on_commit(fn)

    else:
        logger.debug("trigger task %s immediately", celery_task.name)
        fn()


def delay_on_commit(celery_task, *args, **kwargs):
    """
    Star argument version of `apply_async_on_commit`, does not support the extra options.
    """

    apply_async_on_commit(celery_task, args=args, kwargs=kwargs)
