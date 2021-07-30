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
import os

MULTIPROC_ENV_NAME = 'prometheus_multiproc_dir'
DEFAULT_DATA_PATH = '_prometheus_data'


def setup_multiproc_dir(data_path: str = DEFAULT_DATA_PATH):
    """Setup multi processes directory

    :param data_path: if MULTIPROC_ENV_NAME has already been configured in env vars, then the
        data_path parameter won't be used at all
    """
    dirname = os.environ.setdefault(MULTIPROC_ENV_NAME, data_path)
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    except IOError as e:
        print(f'unable to make prometheus data directory: {e}')
