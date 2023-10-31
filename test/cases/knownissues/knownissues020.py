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

if True:
    from steps.common import LogVerificationStep as _LogVerificationStepImpl  # `LogVerificationStep` used for inheritance.


class KnownIssues020(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckScenarioLogExpectations, CheckScenarioReportExpectations, ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Known issue persistence v/s test errors",
            description=(
                "Check that known issues declared at the definition level persist when a test error occurs. "
                "Check the way things are displayed in the console and saved in the scenario report."
            ),
        )
        self.verifies(
            scenario.test.reqs.KNOWN_ISSUES,
            scenario.test.reqs.ERROR_HANDLING,
            scenario.test.reqs.SCENARIO_LOGGING,
            scenario.test.reqs.SCENARIO_REPORT,
        )

        # Execution step.
        self.addstep(ExecScenario(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO,
            # Make the KNOWN_ISSUES_SCENARIO generate an exception.
            config_values={scenario.test.data.scenarios.KnownIssuesScenario.ConfigKey.RAISE_EXCEPTIONS: True},
            generate_report=True,
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))

        # Expectations.
        _scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO, config_values=ExecScenario.getinstance().config_values,
            # Checks the first step is being executed, but not the ones after.
            steps=True, stats=True,
            # Error details makes the step check both the exception raised, and the warnings, i.e. known issues.
            error_details=True,
        )  # type: scenario.test.ScenarioExpectations

        # Verification steps.
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), _scenario_expectations))
        self.addstep(CheckKnownIssuesLogOutput(ExecScenario.getinstance()))
        self.addstep(CheckScenarioReportExpectations(ExecScenario.getinstance(), _scenario_expectations))


class CheckKnownIssuesLogOutput(_LogVerificationStepImpl):

    def step(self):  # type: (...) -> None
        self.STEP("Known issues logging output")

        self.RESULT("Before the exception, all known issues are displayed twice:")
        for _issue_id, _message in (
            ("#---", "Known issue in KnownIssuesScenario.__init__()"),
            ("#000", "Known issue in KnownIssuesStep.__init__()"),
            ("#001", "Known issue in KnownIssuesStep.step() before ACTION/RESULT"),
            ("#002", "Known issue in KnownIssuesStep.step() under ACTION"),
        ):  # type: str, str
            _expected_line = f"Issue {_issue_id}! {_message}"  # type: str
            if self.RESULT(f"- {_expected_line}:"):
                self.assertlen(
                    self.assertlines(_expected_line), 2,
                    evidence="Known issue before exception",
                )

        self.RESULT("After the exception, known issues declared at the definition level are displayed once only:")
        for _issue_id, _message in (
            ("#004", "Known issue in KnownIssuesStep.step() after ACTION/RESULT"),
            ("#011", "Known issue in KnownIssuesScenario.step010() before ACTION/RESULT"),
            ("#014", "Known issue in KnownIssuesScenario.step010() after ACTION/RESULT"),
        ):  # Type already declared above.
            _expected_line = f"Issue {_issue_id}! {_message}"  # Type already declared above.
            if self.RESULT(f"- {_expected_line}:"):
                self.assertlen(
                    self.assertlines(_expected_line), 1,
                    evidence="Known issue at definition level after exception",
                )

        self.RESULT("After the exception, known issues declared under action or expected result execution are not displayed:")
        for _issue_id, _message in (
            ("#003", "Known issue in KnownIssuesStep.step() under ACTION"),
            ("#012", "Known issue in KnownIssuesScenario.step010() under ACTION"),
            ("#013", "Known issue in KnownIssuesScenario.step010() under ACTION"),
        ):  # Type already declared above.
            _expected_line = f"Issue {_issue_id}! {_message}"  # Type already declared above.
            if self.RESULT(f"- {_expected_line}:"):
                self.assertnoline(
                    _expected_line,
                    evidence="Known issue under ACTION/RESULT after exception",
                )
