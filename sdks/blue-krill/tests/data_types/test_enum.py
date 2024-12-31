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
from typing import List, Type

import pytest

from blue_krill.contextlib import nullcontext as does_not_raise
from blue_krill.data_types.enum import EnumField, FeatureFlag, FeatureFlagField, StructuredEnum
from tests.utils import generate_random_string


def flag_builder(fields: List[FeatureFlagField]) -> Type[FeatureFlag]:
    return type(
        generate_random_string(16),
        (FeatureFlag,),
        {field.name: field for field in fields},
    )


class TestFeatureFlags:
    def test_make_empty_flag(self):
        with pytest.raises(ValueError):
            flag_builder([FeatureFlagField(name="")])

    def test_register_empty_flag(self):
        flag = flag_builder([])
        with pytest.raises(ValueError):
            flag.register_feature_flag(FeatureFlagField())
        with pytest.raises(ValueError):
            flag.register_feature_flag(FeatureFlagField(name=""))

    @pytest.mark.parametrize(
        "init_fields, str_var, expected",
        [
            ([], "foo", pytest.raises(ValueError)),
            ([FeatureFlagField(name="foo")], "foo", does_not_raise()),
            ([FeatureFlagField(name="foo")], "bar", pytest.raises(ValueError)),
        ],
    )
    def test_cast(self, init_fields, str_var, expected):
        flags = flag_builder(init_fields)
        with expected:
            flag = flags(str_var)
            assert getattr(flags, str_var) == flag

    @pytest.mark.parametrize(
        "init_fields, expected",
        [
            ([], {}),
            ([FeatureFlagField(name="foo")], {"foo": False}),
            (
                [
                    FeatureFlagField(name="foo"),
                    FeatureFlagField(name="bar", label="baz"),
                ],
                {"foo": False, "bar": False},
            ),
            (
                [
                    FeatureFlagField(name="foo"),
                    FeatureFlagField(name="baz", label="baz", default=False),
                ],
                {"foo": False, "baz": False},
            ),
            (
                [
                    FeatureFlagField(name="foo"),
                    FeatureFlagField(name="bar", label="bar"),
                    FeatureFlagField(name="baz", label="baz", default=True),
                ],
                {"foo": False, "bar": False, "baz": True},
            ),
        ],
    )
    def test_get_default_flags(self, init_fields, expected):
        assert flag_builder(init_fields).get_default_flags() == expected

    @pytest.mark.parametrize(
        "init_fields, expected",
        [
            ([], []),
            ([FeatureFlagField(name="foo")], [("foo", "foo")]),
            (
                [
                    FeatureFlagField(name="foo"),
                    FeatureFlagField(name="bar", label="baz"),
                ],
                [("foo", "foo"), ("bar", "baz")],
            ),
        ],
    )
    def test_get_django_choices(self, init_fields, expected):
        assert flag_builder(init_fields).get_django_choices() == expected

    @pytest.mark.parametrize(
        "init_fields, to_register, expected",
        [
            ([], FeatureFlagField(name="foo"), does_not_raise()),
            (
                [FeatureFlagField(name="foo")],
                FeatureFlagField(name="foo", label="foo"),
                does_not_raise(),
            ),
            (
                [FeatureFlagField(name="foo")],
                FeatureFlagField(name="foo", label="bar"),
                pytest.raises(ValueError),
            ),
        ],
    )
    def test_register_feature_flag(self, init_fields, to_register, expected):
        flags = flag_builder(init_fields)
        with expected:
            flags.register_feature_flag(to_register)
            assert flags.get_feature_label(to_register.name) == to_register.label

        assert to_register.name in list(flags)

    @pytest.mark.parametrize(
        "init_fields, expected",
        [
            ([], []),
            ([FeatureFlagField(name="foo")], ["foo"]),
            (
                [
                    FeatureFlagField(name="foo"),
                    FeatureFlagField(name="bar", label="baz"),
                ],
                ["foo", "bar"],
            ),
            (
                [
                    FeatureFlagField(name="bar", label="baz"),
                    FeatureFlagField(name="foo"),
                ],
                ["bar", "foo"],
            ),
        ],
    )
    def test_iter(self, init_fields, expected):
        flags = flag_builder(init_fields)
        assert list(flags) == expected


class UserType(StructuredEnum):
    NORMAL = EnumField(1, label="normal user")
    ADMIN = EnumField(2, label="admin")
    CORE_DEVELOPER = EnumField(3)
    NOBODY = 4
    RESERVED_USER = EnumField(5, is_reserved=True)

    def foo(self):
        """Regular method should be ignored in choices"""
        return "foo"


class ProgrammingLanguage(StructuredEnum):
    HIGH_LEVEL = EnumField(["Python", "Go"], label="high-level language")
    LOW_LEVEL = EnumField(["C", "C++"], label="low-level language")
    THE_BEST = EnumField("Python", label="the best language")


class TestStructuredEnum:
    def test_get_django_choices(self):
        assert UserType.get_django_choices() == [
            (1, "normal user"),
            (2, "admin"),
            (3, "Core developer"),
            (4, "Nobody"),
        ]

    def test_get_choices(self):
        assert UserType.get_choices() == [
            (1, "normal user"),
            (2, "admin"),
            (3, "Core developer"),
            (4, "Nobody"),
        ]

    def test_get_choices_for_unhashable(self):
        assert ProgrammingLanguage.get_choices() == [
            (["Python", "Go"], "high-level language"),
            (["C", "C++"], "low-level language"),
            ("Python", "the best language"),
        ]

    @pytest.mark.parametrize(
        "value,label",
        [
            (UserType.NORMAL, "normal user"),
            (3, "Core developer"),
            (4, "Nobody"),
            (5, 5),
        ],
    )
    def test_get_choice_label(self, value, label):
        assert UserType.get_choice_label(value) == label

    @pytest.mark.parametrize(
        "value,label",
        [
            (ProgrammingLanguage.HIGH_LEVEL, "high-level language"),
            (["C", "C++"], "low-level language"),
            (ProgrammingLanguage.THE_BEST, "the best language"),
        ],
    )
    def test_get_choice_label_for_unhashable(self, value, label):
        assert ProgrammingLanguage.get_choice_label(value) == label

    def test_get_labels(self):
        assert UserType.get_labels() == ["normal user", "admin", "Core developer", "Nobody"]

    def test_get_values(self):
        assert UserType.get_values() == [1, 2, 3, 4]


try:
    from blue_krill.data_types.enum import StrStructuredEnum, IntStructuredEnum
except ImportError:
    pass
else:
    class StrDemoEnum(StrStructuredEnum):
        FOO = "foo"
        BAR = "bar"

    class TestStrStructuredEnum:
        def test_value_compare(self):
            assert StrDemoEnum.FOO == "foo"
            assert StrDemoEnum.BAR.value == "bar"

        def test_string_formatting(self):
            assert str(StrDemoEnum.BAR) == "bar"
            assert "%s" % StrDemoEnum.FOO == "foo"
            assert "{}".format(StrDemoEnum.BAR) == "bar"
            assert f"{StrDemoEnum.FOO}-{StrDemoEnum.BAR}" == "foo-bar"

    class IntDemoEnum(IntStructuredEnum):
        FOO = 1
        BAR = 2

    class TestIntStructuredEnum:
        def test_value_compare(self):
            assert IntDemoEnum.FOO == 1
            assert IntDemoEnum.BAR.value == 2

        def test_string_formatting(self):
            assert str(IntDemoEnum.BAR) == "2"
            assert "%s" % IntDemoEnum.FOO == "1"
            assert "{}".format(IntDemoEnum.BAR) == "2"
            assert f"{IntDemoEnum.FOO}-{IntDemoEnum.BAR}" == "1-2"
