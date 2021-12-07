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

import re
from typing import Callable, Iterable

__all__ = ["RegexCubingHelper", "CommonCaseRegexPatterns", "CommonCaseConvertor", "shortcuts"]


class RegexCubingHelper:
    """The best way to resolve a Rubik's cube is to take it apart and put it back together."""

    def __init__(self, patterns: Iterable[str]):
        self._pattern = re.compile("|".join(patterns))

    def cubing(self, string: str, transform_fn: Callable[[Iterable[str]], Iterable[str]], sep: str) -> str:
        """Join the string with the given separator and transform the parts."""

        parts = (i for i in self._pattern.split(string) if i)
        return sep.join((i for i in transform_fn(parts) if i))

    def cubing_capitalize_case(self, string: str, sep: str) -> str:
        """Join the string with the given separator and capitalize the parts."""

        return self.cubing(string, lambda parts: (i.capitalize() for i in parts), sep)

    def cubing_lower_case(self, string: str, sep: str) -> str:
        """Join the string with the given separator and lower case the parts."""

        return self.cubing(string, lambda parts: (i.lower() for i in parts), sep)

    def cubing_upper_case(self, string: str, sep: str) -> str:
        """Join the string with the given separator and upper case the parts."""

        return self.cubing(string, lambda parts: (i.upper() for i in parts), sep)


class CommonCaseRegexPatterns:
    """The regex pattern for common case."""

    CAMELCASE = r"(?<=[^A-Z])(?=[A-Z])"
    SNAKECASE = r"_+"
    DASHCASE = r"-+"
    DOTCASE = r"\.+"
    SPACECASE = r" +"


class CommonCaseConvertor:
    """The convertor for common case."""

    def __init__(self, patterns: Iterable[str]):
        self._helper = RegexCubingHelper(patterns)

    def to_camel_case(self, string: str) -> str:
        """
        Convert the string to camel case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_camel_case("Cubing Case")
        'CubingCase'
        """

        return self._helper.cubing_capitalize_case(string, "")

    def to_lower_camel_case(self, string: str) -> str:
        """Convert the string to lower camel case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_lower_camel_case("Cubing Case")
        'cubingCase'
        """

        def transform(parts):
            for index, part in enumerate(parts):
                if index == 0:
                    yield part.lower()
                else:
                    yield part.capitalize()

        return self._helper.cubing(string, transform, "")

    def to_lower_snake_case(self, string: str) -> str:
        """
        Convert the string to lower snake case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_lower_snake_case("Cubing Case")
        'cubing_case'
        """

        return self._helper.cubing_lower_case(string, "_")

    def to_upper_snake_case(self, string: str) -> str:
        """
        Convert the string to upper snake case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_upper_snake_case("Cubing Case")
        'CUBING_CASE'
        """

        return self._helper.cubing_upper_case(string, "_")

    def to_lower_dash_case(self, string: str) -> str:
        """
        Convert the string to lower dash case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_lower_dash_case("Cubing Case")
        'cubing-case'
        """

        return self._helper.cubing_lower_case(string, "-")

    def to_upper_dash_case(self, string: str) -> str:
        """Convert the string to upper dash case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_upper_dash_case("Cubing Case")
        'CUBING-CASE'
        """

        return self._helper.cubing_upper_case(string, "-")

    def to_lower_dot_case(self, string: str) -> str:
        """Convert the string to lower dot case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_lower_dot_case("Cubing Case")
        'cubing.case'
        """

        return self._helper.cubing_lower_case(string, ".")

    def to_capitalize_dot_case(self, string: str) -> str:
        """Convert the string to upper dot case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_capitalize_dot_case("Cubing Case")
        'Cubing.Case'
        """

        return self._helper.cubing_capitalize_case(string, ".")

    def to_lower_space_case(self, string: str) -> str:
        """Convert the string to lower space case, like this:
        >>> convertor = CommonCaseConvertor([CommonCaseRegexPatterns.SPACECASE])
        >>> convertor.to_lower_space_case("Cubing Case")
        'cubing case'
        """

        return self._helper.cubing_lower_case(string, " ")


shortcuts = CommonCaseConvertor(
    (
        CommonCaseRegexPatterns.CAMELCASE,
        CommonCaseRegexPatterns.SNAKECASE,
        CommonCaseRegexPatterns.DASHCASE,
        CommonCaseRegexPatterns.DOTCASE,
        CommonCaseRegexPatterns.SPACECASE,
    )
)
