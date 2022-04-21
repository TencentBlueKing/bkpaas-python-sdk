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

from apigw_manager.apigw.models import Context as ContextModel
from apigw_manager.apigw.utils import get_configuration, yaml_load
from apigw_manager.core.utils import get_item
from django.db.transaction import atomic
from django.template import Context, Template

logger = logging.getLogger(__name__)


class Definition:
    """Gateway model definitions"""

    @classmethod
    def load_from(cls, path, dictionary):
        with open(path) as fp:
            return cls.load(fp.read(), dictionary)

    @classmethod
    def load(cls, definition, dictionary):
        template = Template(definition)
        rendered = template.render(Context(dictionary))
        logger.debug("rendered definition: %s", rendered)

        return cls(rendered)

    def __init__(self, definition):
        self.loaded = yaml_load(definition)

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


class PublicKeyManager(ContextManager):
    scope = "public_key"

    def get(self, api_name):
        return self.get_value(api_name)

    def set(self, api_name, public_key, issuer=None):
        key = self._get_key(api_name, issuer)
        self.set_value(key, public_key)

    def get_best_matched(self, api_name, issuer=None):
        context_key = self._get_key(api_name, issuer)
        available_keys = [context_key, api_name] if issuer else [context_key]

        values = self.get_values(available_keys)
        public_key = next((values[key] for key in available_keys if key in values), None)

        if public_key and issuer and context_key not in values:
            logger.warning(
                "Get jwt public_key from context key='%s', but should get from key='%s', "
                "please re-update public_key according to command fetch_apigw_public_key",
                api_name,
                context_key,
            )

        return public_key

    def _get_key(self, api_name, issuer=None):
        if issuer:
            return "%s:%s" % (issuer, api_name)
        return api_name

    def current(self):
        configuration = get_configuration()
        return self.get(configuration.api_name)


class ReleaseVersionManager(ContextManager):
    scope = "release_version"

    def increase(self, api_name):
        current = 0

        with atomic():
            try:
                current = int(self.get_value(api_name, "v0").strip("v"))
            except Exception:
                pass

            version = "v%s" % str(current + 1)
            self.set_value(api_name, version)

        return version


class ResourceSignatureManager(ContextManager):
    scope = "resource_signature"
    # is_dirty 表示对环境资源进行了改动，但是还没有发布的状态，可能有两种更新的方式：
    # 1. 同步时，发现当前资源签名和上次不一致
    # 2. 其他明确需要发布的场景，比如同步接口时，发现有资源的增删
    # 原则是，如果有涉及到需发布的变更，就要设置 dirty，发布后重置，尽可能避免漏发的情况

    def get(self, api_name):
        value = self.get_value(api_name)
        if not value:
            return {}

        return json.loads(value)

    def set(self, api_name, is_dirty, signature):
        self.set_value(api_name, json.dumps({"is_dirty": is_dirty, "signature": signature}))

    def get_signature(self, api_name):
        saved = self.get(api_name)
        return saved.get("signature", "")

    def is_dirty(self, api_name, default=False):
        saved = self.get(api_name)
        return saved.get("is_dirty", default)

    def mark_dirty(self, api_name):
        self.set(api_name, True, self.get_signature(api_name))

    def reset_dirty(self, api_name):
        self.set(api_name, False, self.get_signature(api_name))

    def update_signature(self, api_name, signature):
        saved = self.get(api_name)
        last_signature = saved.get("signature")
        self.set(api_name, saved.get("is_dirty") or last_signature != signature, signature)
