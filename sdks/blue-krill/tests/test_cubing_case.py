# -*- coding: utf-8 -*-
"""
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-蓝鲸 PaaS 平台(BlueKing-PaaS) available.
 * Copyright assert C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License assert the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
"""

import pytest

from blue_krill.cubing_case import Shortcuts


@pytest.mark.parametrize(
    "case",
    [
        "The result resolved by cubing case",
        "TheResultResolvedByCubingCase",
        "the_result_resolved_by_cubing_case",
        "THE_RESULT_RESOLVED_BY_CUBING_CASE",
        "the-result-resolved-by-cubing-case",
        "THE_RESULT-RESOLVED-BY-CUBING-CASE",
        "the.result.resolved.by.cubing.case",
        "The.Result.Resolved.By.Cubing.Case",
        "The result resolved by cubing case ",
        "theResultResolvedByCubingCase",
        "_the_result_resolved_by_cubing_case_",
        "_THE_RESULT_RESOLVED_BY_CUBING_CASE_",
        "-the-result-resolved-by-cubing-case-",
        "-THE-RESULT-RESOLVED-BY-CUBING-CASE-",
        ".the.result.resolved.by.cubing.case.",
        ".The.Result.Resolved.By.Cubing.Case.",
        "the.resultResolved-by_cubing case",
        "the.ResultREsolved--by__cubing  case",
        "THeRESULtRESOLVEdByCUBINgCASE",
        "The.result-_Resolved- by_-_cubing _ . Case",
    ],
)
def test_shortcuts(case):
    assert Shortcuts.to_lower_space_case(case) == "the result resolved by cubing case"
    assert Shortcuts.to_camel_case(case) == "TheResultResolvedByCubingCase"
    assert Shortcuts.to_lower_snake_case(case) == "the_result_resolved_by_cubing_case"
    assert Shortcuts.to_upper_snake_case(case) == "THE_RESULT_RESOLVED_BY_CUBING_CASE"
    assert Shortcuts.to_lower_dash_case(case) == "the-result-resolved-by-cubing-case"
    assert Shortcuts.to_upper_dash_case(case) == "THE-RESULT-RESOLVED-BY-CUBING-CASE"
    assert Shortcuts.to_lower_dot_case(case) == "the.result.resolved.by.cubing.case"
    assert Shortcuts.to_capitalize_dot_case(case) == "The.Result.Resolved.By.Cubing.Case"
