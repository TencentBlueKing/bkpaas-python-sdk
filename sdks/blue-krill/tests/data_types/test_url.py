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
from string import ascii_lowercase, digits

import pytest

from blue_krill.data_types.url import MutableURL
from tests.utils import generate_random_string


class TestMutableURL:
    @pytest.fixture
    def part_scheme(self):
        # Python 3.11 开始，限制 scheme 必须以字母开头
        return 'x' + generate_random_string(9)

    @pytest.fixture
    def part_username(self):
        return generate_random_string(10)

    @pytest.fixture
    def part_password(self):
        return generate_random_string(10)

    @pytest.fixture
    def part_hostname(self):
        return generate_random_string(10)

    @pytest.fixture
    def part_port(self):
        return 80

    @pytest.fixture
    def part_path(self):
        return '/' + generate_random_string(chars=(ascii_lowercase + digits + '/'))

    @pytest.fixture
    def url(self, part_scheme, part_username, part_password, part_hostname, part_port, part_path):
        return MutableURL(f"{part_scheme}://{part_username}:{part_password}@{part_hostname}:{part_port}{part_path}")

    def test_sensitive(self, url, part_scheme, part_username, part_password, part_hostname, part_port, part_path):
        assert str(url) == f"{part_scheme}://{part_username}:{part_password}@{part_hostname}:{part_port}{part_path}"
        assert url.obscure() == f"{part_scheme}://{part_username}:********@{part_hostname}:{part_port}{part_path}"
        assert repr(url) == f"MutableURL('{url.obscure()}')"

    def test_replace(self, url, part_scheme, part_username, part_hostname, part_port, part_path):
        new_url = url.replace(password=None)
        assert str(new_url) == f"{part_scheme}://{part_username}@{part_hostname}:{part_port}{part_path}"
        assert new_url.obscure() == str(new_url)

    def test_components(self, url, part_scheme, part_username, part_password, part_hostname, part_port, part_path):
        assert url.scheme == part_scheme
        assert url.username == part_username
        assert url.password == part_password
        assert url.hostname == part_hostname
        assert url.port == part_port
        assert url.netloc == f"{part_username}:{part_password}@{part_hostname}:{part_port}"
        assert url.path == part_path
