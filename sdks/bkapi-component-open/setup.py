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
from setuptools import find_packages, setup

readme = ''

setup(
    description='',
    long_description=readme,
    name='bkapi-component-open',
    version='2.1.0',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
    author='blueking',
    license='MIT',
    packages=find_packages(),
    namespace_packages=['bkapi_component'],
    package_dir={'': '.'},
    package_data={},
    install_requires=[
        'bkapi-client-core>=1.1.0,<2.0.0',
    ],
)
