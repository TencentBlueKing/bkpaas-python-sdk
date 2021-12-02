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
from functools import partial
from typing import Callable, Iterable, cast


def cubing(
    string: str,
    split_fn: Callable[[str], Iterable[str]],
    transform_fn: Callable[[Iterable[str]], Iterable[str]],
    concatenate_fn: Callable[[Iterable[str]], str],
) -> str:
    """The best way to resolve a Rubik's cube is to take it apart and put it back together."""

    parts = (i for i in split_fn(string) if i)
    return concatenate_fn(i for i in transform_fn(parts) if i)


def transform_lower_case(parts: Iterable[str]) -> Iterable[str]:
    """Transform the parts to lower case."""
    return (i.lower() for i in parts)


def transform_upper_case(parts: Iterable[str]) -> Iterable[str]:
    """Transform the parts to upper case."""
    return (i.upper() for i in parts)


def transform_capitalize_case(parts: Iterable[str]) -> Iterable[str]:
    """Transform the parts to capitalize case."""
    return (i.capitalize() for i in parts)


def split_by_regex(patterns: Iterable[str]):
    """Split the string by the given patterns, return the parts that are not in the stop words."""

    return cast(Callable[[str], Iterable[str]], partial(re.split, "|".join(patterns)))


class CaseSplitRegexPattern:
    """The builtin regex pattern use for split_by_regex."""

    CAMELCASE = "(?<=[^A-Z])(?=[A-Z])"
    SNAKECASE = "_+"
    DASHCASE = "-+"
    DOTCASE = "\\.+"
    SENTENCE = " +"

    ALL = (CAMELCASE, SNAKECASE, DASHCASE, DOTCASE, SENTENCE)


def join_the_capitalize_case(string: str, sep: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Join the string with the given separator and capitalize the parts."""

    return cubing(string, split_by_regex(patterns), transform_capitalize_case, sep.join)


def join_the_lower_case(string: str, sep: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Join the string with the given separator and lower case the parts."""

    return cubing(string, split_by_regex(patterns), transform_lower_case, sep.join)


def join_the_upper_case(string: str, sep: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Join the string with the given separator and upper case the parts."""

    return cubing(string, split_by_regex(patterns), transform_upper_case, sep.join)


def to_sentence(string: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Convert the string to sentence."""

    def transform(parts: Iterable[str]) -> Iterable[str]:
        for index, part in enumerate(parts):
            if index == 0:
                yield part.capitalize()
            else:
                yield part.lower()

    return cubing(string, split_by_regex(patterns), transform, " ".join)


def to_camel_case(string: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Convert the string to camel case."""

    return join_the_capitalize_case(string, "")


def to_lower_snake_case(string: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Convert the string to lower snake case."""

    return join_the_lower_case(string, "_")


def to_upper_snake_case(string: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Convert the string to upper snake case."""

    return join_the_upper_case(string, "_")


def to_lower_dash_case(string: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Convert the string to lower dash case."""

    return join_the_lower_case(string, "-")


def to_upper_dash_case(string: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Convert the string to upper dash case."""

    return join_the_upper_case(string, "-")


def to_lower_dot_case(string: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Convert the string to lower dot case."""

    return join_the_lower_case(string, ".")


def to_capitalize_dot_case(string: str, patterns: Iterable[str] = CaseSplitRegexPattern.ALL) -> str:
    """Convert the string to upper dot case."""

    return join_the_capitalize_case(string, ".")
