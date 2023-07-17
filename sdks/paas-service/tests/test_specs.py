# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except
in compliance with the License. You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific language governing permissions and
limitations under the License.

We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""
import random

from django.db import IntegrityError
from django.test import TestCase
from django_dynamic_fixture import G
from paas_service import models


class TestSpecs(TestCase):
    def setUp(self) -> None:
        self.service: 'models.Service' = G(models.Service)
        self.plan: 'models.Plan' = G(models.Plan, service=self.service)

        self.definition: 'models.SpecDefinition' = G(models.SpecDefinition, name="x", display_name_zh_cn=None)
        self.service.specifications.add(self.definition)

        self.specification: 'models.Specification' = G(
            models.Specification, value="0", definition=self.definition, display_name_zh_cn=None
        )
        self.plan.specifications.add(self.specification)

    def test_display_name(self):
        self.assertEqual("x", self.definition.display_name_zh_cn)
        self.assertEqual("0", self.specification.display_name_zh_cn)

    def test_full_specifications(self):
        definition1: 'models.SpecDefinition' = G(models.SpecDefinition, name="none")
        self.service.specifications.add(definition1)

        definition2: 'models.SpecDefinition' = G(models.SpecDefinition, name="miss")
        specification: 'models.Specification' = G(models.Specification, value="1", definition=definition2)
        self.plan.specifications.add(specification)

        self.assertDictEqual(self.plan.full_specifications, {"x": "0", "none": None})

    def test_specification_unique(self):
        with self.assertRaises(IntegrityError):
            models.Specification.objects.create(value=self.specification.value, definition=self.definition)

    def test_definition_unique(self):
        with self.assertRaises(IntegrityError):
            models.SpecDefinition.objects.create(name=self.definition.name)

    def test_ordering(self):
        for i in range(100):
            G(models.SpecDefinition, index=random.randint(0, 100))

        last = 0
        for spec in models.SpecDefinition.objects.all():
            self.assertLessEqual(last, spec.index)
            last = spec.index
