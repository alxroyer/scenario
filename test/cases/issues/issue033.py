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

import scenario.test
import scenario.text

if True:
    # `ScenarioReportFileVerificationStep` used for inheritance.
    from scenarioreport.steps.reportfile import ScenarioReportFileVerificationStep as _ScenarioReportFileVerificationStepImpl


class Issue33(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Issue #33! Fully qualified name for code locations",
            description="Check that code locations for errors and known issues give the fully qualified names of the methods they occur in.",
        )
        self.verifies(
            scenario.test.reqs.ERROR_HANDLING,
            scenario.test.reqs.KNOWN_ISSUES,
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


class CheckExceptionLocation(_ScenarioReportFileVerificationStepImpl):

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            index,  # type: int
            expected_fqn,  # type: str
    ):  # type: (...) -> None
        _ScenarioReportFileVerificationStepImpl.__init__(self, exec_step)

        self.index = index  # type: int
        self.expected_fqn = expected_fqn  # type: str

    def step(self):  # type: (...) -> None
        from scenario._jsondictutils import JsonDict  # noqa  ## Access to protected module

        self.STEP("Exception location")

        _json_error = {}  # type: scenario.types.JsonDict
        if self.ACTION(f"Get the {scenario.text.ordinal(self.index)} error info from the scenario report."):
            _json_error = self.assertjson(
                JsonDict.readfile(self.report_path), f"errors[{self.index}]", type=dict,
                evidence="Error info",
            )

        if self.RESULT(f"The error location gives the fully qualified name of the method the exception occurred in: '{self.expected_fqn}'."):
            self.assertendswith(
                self.assertjson(_json_error, "location", type=str), f":{self.expected_fqn}",
                evidence="Error location",
            )


class CheckKnownIssueLocation(_ScenarioReportFileVerificationStepImpl):

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            index,  # type: int
            expected_fqn,  # type: str
    ):  # type: (...) -> None
        _ScenarioReportFileVerificationStepImpl.__init__(self, exec_step)

        self.index = index  # type: int
        self.expected_fqn = expected_fqn  # type: str

    def step(self):  # type: (...) -> None
        from scenario._jsondictutils import JsonDict  # noqa  ## Access to protected module

        self.STEP("Known issue location")

        _json_known_issue = {}  # type: scenario.types.JsonDict
        if self.ACTION(f"Get the {scenario.text.ordinal(self.index)} known issue info from the scenario report."):
            _json_known_issue = self.assertjson(
                JsonDict.readfile(self.report_path), f"warnings[{self.index}]", type=dict,
                evidence="Known issue info",
            )

        if self.RESULT(f"The known issue location gives the fully qualified name of the method it has been registered in: '{self.expected_fqn}'."):
            self.assertendswith(
                self.assertjson(_json_known_issue, "location", type=str), f":{self.expected_fqn}",
                evidence="Known issue location",
            )
