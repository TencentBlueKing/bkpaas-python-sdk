# -*- coding: utf-8 -*-
# TencentBlueKing is pleased to support the open source community by making
# 蓝鲸智云 - PaaS 平台 (BlueKing - PaaS System) available.
# Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions and
# limitations under the License.
#
# We undertake not to change the open source license (MIT license) applicable
# to the current version of the project delivered to anyone in the future.

import pytest

from blue_krill.monitoring.probe.base import DiagnosisReport, DiagnosisReportList, Issue, NoFatalIssueError


class TestDiagnosisReport:
    @pytest.mark.parametrize(
        ("issues", "expected"),
        [
            ([], (True, True)),
            ([Issue(fatal=False, description="")], (False, True)),
            ([Issue(fatal=True, description="")], (False, False)),
            ([Issue(fatal=False, description=""), Issue(fatal=True, description="")], (False, False)),
        ],
    )
    def test_init(self, issues, expected):
        report = DiagnosisReport("", issues=issues)
        assert (issues, *expected) == (report.issues, report.healthy, report.alive)

    @pytest.mark.parametrize(
        ("issues", "expected"),
        [
            ([], (True, True)),
            ([Issue(fatal=False, description="")], (False, True)),
            ([Issue(fatal=True, description="")], (False, False)),
            ([Issue(fatal=False, description=""), Issue(fatal=True, description="")], (False, False)),
        ],
    )
    def test_set_issues(self, issues, expected):
        report = DiagnosisReport("")
        report.set_issues(issues)
        assert (issues, *expected) == (report.issues, report.healthy, report.alive)

    @pytest.mark.parametrize(
        ("issues", "expected"),
        [
            pytest.param([], [], marks=pytest.mark.xfail(raises=NoFatalIssueError)),
            pytest.param(
                [Issue(fatal=False, description="not fatal")],
                [],
                marks=pytest.mark.xfail(raises=NoFatalIssueError),
            ),
            ([Issue(fatal=True, description="fatal")], [Issue(fatal=True, description="fatal")]),
            (
                [Issue(fatal=False, description="not fatal"), Issue(fatal=True, description="fatal")],
                [Issue(fatal=True, description="fatal")],
            ),
        ],
    )
    def test_get_fatal_issues(self, issues, expected):
        report = DiagnosisReport("")
        report.set_issues(issues)
        assert report.get_fatal_issues() == expected

    @pytest.mark.parametrize(
        ("issues", "expected"),
        [
            pytest.param([], "", marks=pytest.mark.xfail(raises=NoFatalIssueError)),
            pytest.param(
                [Issue(fatal=False, description="not fatal")],
                "",
                marks=pytest.mark.xfail(raises=NoFatalIssueError),
            ),
            ([Issue(fatal=True, description="fatal")], "fatal"),
            (
                [Issue(fatal=False, description="not fatal"), Issue(fatal=True, description="fatal")],
                "fatal",
            ),
            (
                [
                    Issue(fatal=False, description="not fatal"),
                    Issue(fatal=True, description="reason B!"),
                    Issue(fatal=True, description="reason A!"),
                ],
                "reason B!; reason A!",
            ),
        ],
    )
    def test_get_report_message(self, issues, expected):
        report = DiagnosisReport("")
        report.set_issues(issues)
        assert report.get_report_message() == expected


class TestDiagnosisReportList:
    @pytest.mark.parametrize(
        ("reports", "expected"),
        [
            ([DiagnosisReport(system_name="", issues=[Issue(fatal=False, description="")])], False),
            (
                [
                    DiagnosisReport(system_name=""),
                    DiagnosisReport(system_name="", issues=[Issue(fatal=True, description="")]),
                ],
                True,
            ),
            (
                [
                    DiagnosisReport(system_name=""),
                    DiagnosisReport(system_name="", issues=[Issue(fatal=True, description="")], is_core=False),
                ],
                False,
            ),
        ],
    )
    def test_is_death(self, reports, expected):
        assert DiagnosisReportList(reports).is_death == expected

    @pytest.mark.parametrize(
        ("reports", "expected"),
        [
            pytest.param(
                [DiagnosisReport(system_name="a", issues=[Issue(fatal=False, description="")])],
                "",
                marks=pytest.mark.xfail(raises=RuntimeWarning),
            ),
            (
                [
                    DiagnosisReport(system_name="a"),
                    DiagnosisReport(system_name="b", issues=[Issue(fatal=True, description="reason B!")]),
                ],
                {"b": "reason B!"},
            ),
            (
                [
                    DiagnosisReport(system_name="a", issues=[Issue(fatal=True, description="reason A!")]),
                    DiagnosisReport(
                        system_name="b",
                        issues=[
                            Issue(fatal=True, description="reason B-1!"),
                            Issue(fatal=True, description="reason B-2!"),
                        ],
                    ),
                ],
                {"b": "reason B-1!; reason B-2!", "a": "reason A!"},
            ),
        ],
    )
    def test_get_fatal_report(self, reports, expected):
        assert DiagnosisReportList(reports).get_fatal_report() == expected
