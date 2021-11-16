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

from django.db.transaction import atomic
from django.template import Context, Template

from apigw_manager.apigw.models import Context as ContextModel
from apigw_manager.apigw.utils import get_configuration, yaml_load
from apigw_manager.core.utils import get_item

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

    def get(self, namespace):
        """Get the definition according to the namespace"""
        return get_item(self.loaded, self._get_namespace_list(namespace))


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

    def set_value(self, key, value):
        _, created = self.set_context(key, value)

        return created


class PublicKeyManager(ContextManager):
    scope = "public_key"

    def get(self, api_name):
        return self.get_value(api_name)

    def set(self, api_name, public_key):
        self.set_value(api_name, public_key)

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
