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
import json
import logging
from abc import ABC, abstractmethod

from django.conf import settings
from django.db.transaction import atomic
from django.template import Context, Template
from django.utils.module_loading import import_string

from apigw_manager.apigw.models import Context as ContextModel
from apigw_manager.apigw.utils import get_configuration, yaml_load
from apigw_manager.core.utils import get_item

logger = logging.getLogger(__name__)


class Definition:
    """Gateway model definitions"""

    valid_spec_versions = ["1", "2"]
    spec_version = "1"

    @classmethod
    def load_from(cls, path, dictionary):
        with open(path) as fp:
            return cls.load(fp.read(), dictionary)

    @classmethod
    def load(cls, definition, dictionary):
        template = Template(definition)
        rendered = template.render(Context(dictionary, autoescape=False))
        logger.debug("rendered definition: %s", rendered)

        return cls(rendered)

    def __init__(self, definition):
        loaded = yaml_load(definition)

        self._check_spec_version(loaded)
        self.spec_version = loaded.get("spec_version")
        self.loaded = loaded

    def _check_spec_version(self, definition):
        spec_version = definition.get("spec_version")
        if not spec_version:
            return

        if str(spec_version) not in self.valid_spec_versions:
            raise ValueError("spec_version configured in definition.yaml is wrong, choices: [1,2]")

    def _get_namespace_list(self, namespace):
        if not namespace:
            return []

        return namespace.split(".")

    def get(self, namespace, default=None):
        """Get the definition according to the namespace"""
        try:
            return get_item(self.loaded, self._get_namespace_list(namespace))
        except (KeyError, IndexError):
            return default


class ContextManager:
    scope: str

    def get_context(self, key):
        return ContextModel.objects.filter(scope=self.scope, key=key).last()

    def set_context(self, key, value):
        return ContextModel.objects.update_or_create(
            scope=self.scope,
            key=key,
            defaults={
                "value": value,
            },
        )

    def get_value(self, key, default=None):
        context = self.get_context(key)
        if not context:
            return default

        return context.value

    def get_values(self, keys):
        if not keys:
            return {}
        return dict(ContextModel.objects.filter(scope=self.scope, key__in=keys).values_list("key", "value"))

    def set_value(self, key, value):
        _, created = self.set_context(key, value)

        return created


class BasePublicKeyManager(ABC):
    @abstractmethod
    def get(self, gateway_name, issuer=None):
        return ""

    @abstractmethod
    def set(self, gateway_name, public_key, issuer=None):
        return False

    def get_best_matched(self, gateway_name, issuer=None):
        public_key = self.get(gateway_name, issuer)
        if public_key:
            return public_key

        if issuer:
            logger.warning(
                "please re-update %s public_key according to command fetch_apigw_public_key",
                gateway_name,
            )

        return self.get(gateway_name, issuer=None)

    def current(self):
        configuration = get_configuration()
        return self.get(configuration.gateway_name)


class PublicKeyManager(ContextManager, BasePublicKeyManager):
    scope = "public_key"

    def get(self, gateway_name, issuer=None):
        key = self._get_key(gateway_name, issuer)
        return self.get_value(key, None)

    def set(self, gateway_name, public_key, issuer=None):
        key = self._get_key(gateway_name, issuer)
        self.set_value(key, public_key)

    def _get_key(self, gateway_name, issuer=None):
        if issuer:
            return "%s:%s" % (issuer, gateway_name)
        return gateway_name


class ReleaseVersionManager(ContextManager):
    scope = "release_version"

    def increase(self, gateway_name):
        current = 0

        with atomic():
            try:
                current = int(self.get_value(gateway_name, "v0").strip("v"))
            except Exception:
                pass

            version = "v%s" % str(current + 1)
            self.set_value(gateway_name, version)

        return version


class ResourceSignatureManager(ContextManager):
    scope = "resource_signature"

    # is_dirty 表示对环境资源进行了改动，但是还没有发布的状态，可能有两种更新的方式：
    # 1. 同步时，发现当前资源签名和上次不一致
    # 2. 其他明确需要发布的场景，比如同步接口时，发现有资源的增删
    # 原则是，如果有涉及到需发布的变更，就要设置 dirty，发布后重置，尽可能避免漏发的情况

    def get(self, gateway_name):
        value = self.get_value(gateway_name)
        if not value:
            return {}

        return json.loads(value)

    def set(self, gateway_name, is_dirty, signature):
        self.set_value(gateway_name, json.dumps({"is_dirty": is_dirty, "signature": signature}))

    def get_signature(self, gateway_name):
        saved = self.get(gateway_name)
        return saved.get("signature", "")

    def is_dirty(self, gateway_name, default=False):
        saved = self.get(gateway_name)
        return saved.get("is_dirty", default)

    def mark_dirty(self, gateway_name):
        self.set(gateway_name, True, self.get_signature(gateway_name))

    def reset_dirty(self, gateway_name):
        self.set(gateway_name, False, self.get_signature(gateway_name))

    def update_signature(self, gateway_name, signature):
        saved = self.get(gateway_name)
        last_signature = saved.get("signature")
        self.set(gateway_name, saved.get("is_dirty") or last_signature != signature, signature)


def make_default_public_key_manager() -> BasePublicKeyManager:
    public_key_manager_location = getattr(
        settings,
        "APIGW_JWT_PUBLIC_KEY_MANAGER_CLS",
        "apigw_manager.apigw.helper.PublicKeyManager",
    )

    public_key_manager_cls = import_string(public_key_manager_location)
    return public_key_manager_cls()
