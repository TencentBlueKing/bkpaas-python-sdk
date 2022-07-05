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
from django.core.cache import caches

from apigw_manager.apigw.providers import CachePublicKeyProvider, SettingsPublicKeyProvider


@pytest.fixture()
def django_jwt_cache_name():
    return "test-jwt"


@pytest.fixture()
def django_jwt_cache(settings, django_jwt_cache_name, mocker):
    settings.APIGW_JWT_PUBLIC_KEY_CACHE_MINUTES = 1
    settings.APIGW_JWT_PUBLIC_KEY_CACHE_VERSION = "0"
    settings.APIGW_JWT_PUBLIC_KEY_CACHE_NAME = django_jwt_cache_name

    cache = mocker.MagicMock()
    caches[django_jwt_cache_name] = cache

    try:
        yield cache
    finally:
        del caches[django_jwt_cache_name]


class TestSettingsPublicKeyProvider:
    @pytest.fixture(autouse=True)
    def setup_provider(self):
        self.provider = SettingsPublicKeyProvider("testing")

    def test_default_api_name(self):
        assert self.provider.default_api_name == "testing"

    def test_provide_public_key_not_set(self, settings, api_name):
        assert not hasattr(settings, "APIGW_PUBLIC_KEY")
        assert self.provider.provide(api_name) is None

    def test_provide(self, settings, api_name, public_key):
        settings.APIGW_PUBLIC_KEY = public_key
        assert self.provider.provide(api_name) == public_key


class TestCachePublicKeyProvider:
    def test_default_api_name(self):
        provider = CachePublicKeyProvider("testing")
        assert provider.default_api_name == "testing"

    def test_provide_from_cache(self, api_name, django_jwt_cache):
        jwt_issuer = "blueking"

        def side_effect(key):
            data = {
                "apigw:public_key::%s" % api_name: "testing-01",
                "apigw:public_key:%s:%s" % (jwt_issuer, api_name): "testing-02",
            }
            return data[key]

        django_jwt_cache.get.side_effect = side_effect
        provider = CachePublicKeyProvider("testing")

        assert provider.provide(api_name) == "testing-01"
        assert provider.provide(api_name, jwt_issuer) == "testing-02"

    def test_provide_cache_missed(self, api_name, django_jwt_cache, public_key_in_db):
        django_jwt_cache.get.return_value = None
        provider = CachePublicKeyProvider("testing")

        public_key = provider.provide(api_name)
        assert public_key == public_key_in_db

        django_jwt_cache.set.assert_called_with(
            "apigw:public_key::%s" % api_name,
            public_key_in_db,
            provider.cache_expires,
            provider.cache_version,
        )

        public_key = provider.provide(api_name, "not-exist")
        assert public_key == public_key_in_db

        django_jwt_cache.set.assert_called_with(
            "apigw:public_key:not-exist:%s" % api_name,
            public_key_in_db,
            provider.cache_expires,
            provider.cache_version,
        )
