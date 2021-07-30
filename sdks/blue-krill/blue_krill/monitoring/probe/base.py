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
from dataclasses import dataclass, field
from typing import Dict, List, Type

from .exceptions import NoFatalIssueError

logger = logging.getLogger(__name__)


@dataclass
class Issue:
    # if a issue is fatal means the main function of system is not working
    fatal: bool
    description: str

    def __str__(self):
        return f"fatal<{self.fatal}>-{self.description}"


@dataclass
class DiagnosisReport:
    system_name: str
    # when a system is healthy means all the function of it could work
    # well as expected and without any issue.
    healthy: bool = True
    # alive is a key field for indicating system health
    alive: bool = True
    is_core: bool = True
    issues: List[Issue] = field(default_factory=lambda: [])

    def __str__(self):
        return f"{self.system_name}-healthy<{self.healthy}>-alive{self.alive}"

    def __post_init__(self):
        if self.issues:
            self.set_issues(self.issues)

    def set_issues(self, issues: List[Issue]):
        self.issues = issues
        self.healthy = not bool(issues)
        try:
            self.get_fatal_issues()
        except NoFatalIssueError:
            self.alive = True
        else:
            self.alive = False

    def get_fatal_issues(self) -> List[Issue]:
        fatal_issues = []
        for issue in self.issues:
            if issue.fatal:
                fatal_issues.append(issue)

        if not fatal_issues:
            raise NoFatalIssueError()
        return fatal_issues

    def get_report_message(self) -> str:
        fatal_issues = self.get_fatal_issues()
        reasons = [x.description for x in fatal_issues]
        return "; ".join(reasons)


@dataclass
class DiagnosisReportList:
    items: List[DiagnosisReport]

    @property
    def is_death(self) -> bool:
        """if any core probe give not alive diagnosis"""
        for sub_report in self.items:
            if sub_report.is_core and not sub_report.alive:
                return True

        return False

    def get_fatal_report(self) -> Dict[str, str]:
        if not self.is_death:
            raise RuntimeWarning("there is not death report")

        return {x.system_name: x.get_report_message() for x in self.items if not x.alive}


class VirtualProbe:
    """virtual probe"""

    name: str = ''
    is_core: bool = True

    def report(self) -> DiagnosisReport:
        """report diagnose report"""
        report = DiagnosisReport(system_name=self.name, is_core=self.is_core)
        issues = self.diagnose()
        if issues:
            report.set_issues(issues)
        return report

    def diagnose(self) -> List[Issue]:
        """Make a diagnosis, return the issue list."""
        raise NotImplementedError


@dataclass
class ProbeSet:
    # a ProbeSet has to own one probe at least
    probes: List[Type[VirtualProbe]]

    def examination(self) -> DiagnosisReportList:
        diagnosis_list = []
        for probe_cls in self.probes:
            diagnosis_list.append(probe_cls().report())
        return DiagnosisReportList(diagnosis_list)
