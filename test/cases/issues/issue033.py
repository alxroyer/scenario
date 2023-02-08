# -*- coding: utf-8 -*-

# Copyright 2020-2023 Alexis Royer <https://github.com/alxroyer/scenario>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import typing

if typing.TYPE_CHECKING:
    from scenario.typing import JSONDict
import scenario.test
import scenario.text

# Steps:
from steps.common import ExecScenario
from jsonreport.steps.reportfile import JsonReportFileVerificationStep


class Issue33(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Issue #33! Fully qualified name for code locations",
            objective="Check that code locations for errors and known issues give the fully qualified names of the methods they occur in.",
            features=[scenario.test.features.ERROR_HANDLING, scenario.test.features.KNOWN_ISSUES],
        )

        self.section("Exception")
        self.addstep(ExecScenario(
            scenario.test.paths.FAILING_SCENARIO, expected_return_code=scenario.ErrorCode.TEST_ERROR, generate_report=True,
        ))
        self.addstep(CheckExceptionLocation(ExecScenario.getinstance(0), 0, "FailingScenario.step010"))

        self.section("Known issue")
        self.addstep(ExecScenario(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO, generate_report=True,
        ))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 0, "KnownIssuesScenario.__init__"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 1, "KnownIssuesScenario.KnownIssuesStep.__init__"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 2, "KnownIssuesScenario.KnownIssuesStep.step"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 3, "KnownIssuesScenario.KnownIssuesStep.step"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 4, "KnownIssuesScenario.KnownIssuesStep.step"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 5, "KnownIssuesScenario.KnownIssuesStep.step"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 6, "KnownIssuesScenario.step010"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 7, "KnownIssuesScenario.step010"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 8, "KnownIssuesScenario.step010"))
        self.addstep(CheckKnownIssueLocation(ExecScenario.getinstance(1), 9, "KnownIssuesScenario.step010"))


class CheckExceptionLocation(JsonReportFileVerificationStep):

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            index,  # type: int
            expected_fqn,  # type: str
    ):  # type: (...) -> None
        JsonReportFileVerificationStep.__init__(self, exec_step)

        self.index = index  # type: int
        self.expected_fqn = expected_fqn  # type: str

    def step(self):  # type: (...) -> None
        self.STEP("Exception location")

        _json_error = {}  # type: JSONDict
        if self.ACTION(f"Get the {scenario.text.ordinal(self.index)} error info from the JSON report"):
            _json_error = self.assertjson(
                json.loads(self.report_path.read_bytes()), f"errors[{self.index}]", type=dict,
                evidence="Error info",
            )

        if self.RESULT(f"The error location gives the fully qualified name of the method the exception occurred in: '{self.expected_fqn}'."):
            self.assertendswith(
                self.assertjson(_json_error, "location", type=str), f":{self.expected_fqn}",
                evidence="Error location",
            )


class CheckKnownIssueLocation(JsonReportFileVerificationStep):

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            index,  # type: int
            expected_fqn,  # type: str
    ):  # type: (...) -> None
        JsonReportFileVerificationStep.__init__(self, exec_step)

        self.index = index  # type: int
        self.expected_fqn = expected_fqn  # type: str

    def step(self):  # type: (...) -> None
        self.STEP("Known issue location")

        _json_known_issue = {}  # type: JSONDict
        if self.ACTION(f"Get the {scenario.text.ordinal(self.index)} known issue info from the JSON report"):
            _json_known_issue = self.assertjson(
                json.loads(self.report_path.read_bytes()), f"warnings[{self.index}]", type=dict,
                evidence="Known issue info",
            )

        if self.RESULT(f"The known issue location gives the fully qualified name of the method it has been registered in: '{self.expected_fqn}'."):
            self.assertendswith(
                self.assertjson(_json_known_issue, "location", type=str), f":{self.expected_fqn}",
                evidence="Known issue location",
            )
