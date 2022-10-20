# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

# Steps:
from steps.common import ExecScenario
from steps.common import ParseScenarioLog, CheckScenarioLogExpectations
from steps.common import LogVerificationStep
# Related scenarios:
from knownissuesscenario import KnownIssuesScenario


class KnownIssues110(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Known issues - relax mode, with exception",
            objective=(
                "Check that known issues declared at the definition level persist when an error occurs. "
                "Check the way the things are displayed in the console."
            ),
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.ERROR_HANDLING, scenario.test.features.SCENARIO_LOGGING],
        )

        self.addstep(ExecScenario(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO,
            # Make the KNOWN_ISSUES_SCENARIO generate an exception.
            config_values={KnownIssuesScenario.ConfigKey.RAISE_EXCEPTIONS: "1"},
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO, configs={KnownIssuesScenario.ConfigKey.RAISE_EXCEPTIONS: "1"},
            # Checks the first step is being executed, but not the ones after.
            steps=True, stats=True,
            # Error details makes the step check both the exception raised, and the warnings, i.e. known issues.
            error_details=True,
        )))
        self.addstep(CheckKnownIssuesLogOutput(ExecScenario.getinstance()))


class CheckKnownIssuesLogOutput(LogVerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Known issues logging output")

        self.RESULT("Before the exception, all known issues are displayed twice:")
        for _issue_id, _message in (
            ("#---", "Known issue in KnownIssuesScenario.__init__()"),
            ("#000", "Known issue in KnownIssuesStep.__init__()"),
            ("#001", "Known issue in KnownIssuesStep.step() before ACTION/RESULT"),
            ("#002", "Known issue in KnownIssuesStep.step() under ACTION"),
        ):  # type: str, str
            _expected_line = "Issue %s! %s" % (_issue_id, _message)  # type: str
            if self.RESULT("- %s:" % _expected_line):
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
            _expected_line = "Issue %s! %s" % (_issue_id, _message)  # Type already declared above.
            if self.RESULT("- %s:" % _expected_line):
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
            _expected_line = "Issue %s! %s" % (_issue_id, _message)  # Type already declared above.
            if self.RESULT("- %s:" % _expected_line):
                self.assertnoline(
                    _expected_line,
                    evidence="Known issue under ACTION/RESULT after exception",
                )
