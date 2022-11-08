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
        for i in models.SpecDefinition.objects.all():
            self.assertLessEqual(last, i.index)
            last = i.index
