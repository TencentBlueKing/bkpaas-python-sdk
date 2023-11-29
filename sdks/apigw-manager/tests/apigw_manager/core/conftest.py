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
import pytest
from faker import Faker
from pytest_mock import MockerFixture

from apigw_manager.core import configuration


@pytest.fixture()
def config():
    return configuration.Configuration()


@pytest.fixture()
def bk_app_code(faker: Faker, config: configuration.Configuration):
    config.bk_app_code = faker.color
    return config.bk_app_code


@pytest.fixture()
def bk_app_secret(faker: Faker, config: configuration.Configuration):
    config.bk_app_secret = faker.ssn
    return config.bk_app_secret


@pytest.fixture()
def api_cache(mocker: MockerFixture, config: configuration.Configuration):
    config.api_cache = mocker.MagicMock()
    return config.api_cache


@pytest.fixture()
def api_instance(mocker: MockerFixture, config: configuration.Configuration):
    return mocker.MagicMock()
