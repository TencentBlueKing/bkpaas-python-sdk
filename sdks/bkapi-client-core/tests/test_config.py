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
from collections import namedtuple

import pytest

from bkapi_client_core.config import Settings


@pytest.fixture()
def env():
    return {}


@pytest.fixture()
def django_settings(faker):
    FakeSettings = namedtuple("FakeSettings", ["SETTINGS"])
    return FakeSettings(faker.pystr())


class TestDefaultsSettings:
    @pytest.fixture(autouse=True)
    def setup(self, env):
        self.settings = Settings()

    def test_set_defaults_with_position_arg(self):
        self.settings.set_defaults(
            {
                "KEY": "VALUE",
            }
        )
        assert self.settings.get("KEY") == "VALUE"

    def test_set_defaults_with_keyword_arg(self):
        self.settings.set_defaults(KEY="VALUE")
        assert self.settings.get("KEY") == "VALUE"


class TestEnvSettings:
    @pytest.fixture(autouse=True)
    def setup(self, env):
        self.settings = Settings(env=env)

    def test_get_no_exists_in_env(self):
        assert self.settings.get("XXXXX") is None

    def test_get_no_exists_in_env_with_defaults(self):
        assert self.settings.get("XXXXX", 1) == 1

    def test_get_exists_in_env(self, env, faker):
        env["ENV"] = faker.pystr()
        assert self.settings.get("ENV") == env["ENV"]

    def test_get_exists_in_env_with_defaults(self, env, faker):
        env["ENV"] = faker.pystr()
        assert self.settings.get("ENV", "xxxx") == env["ENV"]

    def test_declare_aliases_in_env(self, env, faker):
        env["ENV"] = faker.pystr()

        assert self.settings.get("XXX") is None

        self.settings.declare_aliases("XXX", ["ENV"])
        assert self.settings.get("XXX") == env["ENV"]

    def test_aliases_ordering_in_env(self, env, faker):
        env["X1"] = faker.pystr()
        env["X2"] = faker.pystr()
        self.settings.declare_aliases("X", ["X1", "X2"])
        assert self.settings.get("X") == env["X1"]

        env["Y2"] = faker.pystr()
        self.settings.declare_aliases("Y", ["Y1", "Y2"])
        assert self.settings.get("Y") == env["Y2"]

    def test_defaults(self, env):
        env["VAR_IN_ENV"] = "x1"
        self.settings.set_defaults(VAR_IN_DEFAULTS="x2")

        assert self.settings.get("VAR_IN_ENV") == "x1"
        assert self.settings.get("VAR_IN_DEFAULTS") == "x2"


class TestDjangoSettings(TestEnvSettings):
    @pytest.fixture(autouse=True)
    def setup(self, env, django_settings):
        self.settings = Settings(env=env, settings=django_settings)

    def test_get_no_exists_in_settings(self):
        assert self.settings.get("XXXXX") is None

    def test_get_no_exists_in_settings_with_defaults(self):
        assert self.settings.get("XXXXX", 1) == 1

    def test_get_exists_in_settings(self, django_settings):
        assert self.settings.get("SETTINGS") == django_settings.SETTINGS

    def test_get_exists_in_settings_with_defaults(self, django_settings):
        assert self.settings.get("SETTINGS", "xxxx") == django_settings.SETTINGS

    def test_declare_aliases_in_settings(self, django_settings):
        assert self.settings.get("XXX") is None

        self.settings.declare_aliases("XXX", ["SETTINGS"])
        assert self.settings.get("XXX") == django_settings.SETTINGS

    def test_ordering(self, django_settings, env, faker):
        env["SETTINGS"] = faker.pystr()
        env["ENV"] = faker.pystr()

        assert self.settings.get("SETTINGS") == django_settings.SETTINGS
        assert self.settings.get("ENV") == env["ENV"]

    def test_defaults(self, django_settings):
        self.settings.set_defaults(VAR_IN_DEFAULTS="x2")

        assert self.settings.get("SETTINGS") == django_settings.SETTINGS
        assert self.settings.get("VAR_IN_DEFAULTS") == "x2"
