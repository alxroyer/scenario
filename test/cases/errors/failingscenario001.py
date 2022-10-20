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

import pathlib

import scenario
import scenario.test

# Steps:
from steps.common import ExecScenario
from steps.common import ParseScenarioLog, CheckScenarioLogExpectations
from steps.common import CheckJsonReportExpectations
from steps.common import LogVerificationStep


class FailingScenario001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Failing scenario execution",
            objective=(
                "Check a scenario ends in error as soon as an exception is thrown. "
                "Check the error is displayed and stored appropriately."
            ),
            features=[scenario.test.features.ERROR_HANDLING, scenario.test.features.SCENARIO_LOGGING, scenario.test.features.SCENARIO_REPORT],
        )

        self.scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.FAILING_SCENARIO,
            # Generate the expectation details about steps, actions and expected results, in order to check how the error affects them.
            steps=True, actions_results=True,
            # Check details about error info and statistics as well.
            error_details=True, stats=True,
        )  # type: scenario.test.ScenarioExpectations

        self.addstep(ExecScenario(scenario.test.paths.FAILING_SCENARIO, generate_report=True, expected_return_code=scenario.ErrorCode.TEST_ERROR))
        # Log output.
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), self.scenario_expectations))
        self.addstep(CheckLogOutputExceptionDisplay(ExecScenario.getinstance()))
        # JSON report.
        self.addstep(CheckJsonReportExpectations(ExecScenario.getinstance(), self.scenario_expectations))
        self.addstep(CheckJsonReportExceptionStorage(CheckJsonReportExpectations.getinstance()))

    @property
    def error_location(self):  # type: (...) -> scenario.CodeLocation
        assert self.scenario_expectations.errors and (len(self.scenario_expectations.errors) == 1)
        assert self.scenario_expectations.errors[0].location
        return scenario.CodeLocation.fromlongstring(self.scenario_expectations.errors[0].location)


class CheckLogOutputExceptionDisplay(LogVerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Log output error display")

        if self.RESULT("The exception info is displayed twice."):
            self.assertlinecount(
                "AssertionError: This is an exception.", 2,
                evidence="Error type",
            )
        if self.RESULT("The error location is displayed twice by the way, as regular traceback lines."):
            _error_location = "File \"%s\", line %d, in %s" % (
                # Use a `pathlib.Path` object in order to ensure a path display consistent with the current environment:
                pathlib.Path(scenario.test.paths.FAILING_SCENARIO),
                FailingScenario001.getinstance().error_location.line,
                FailingScenario001.getinstance().error_location.qualname,
            )  # type: str
            self.assertlinecount(
                _error_location, 2,
                evidence="Error location",
            )
        if self.RESULT("Each exception display is delimited with the '!!! EXCEPTION !!!' pattern before and after."):
            self.assertlinecount(
                "!!! EXCEPTION !!!", 4,
                evidence="Exception patterns",
            )


class CheckJsonReportExceptionStorage(scenario.test.VerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("JSON report error storage")

        if self.RESULT("The error is stored with the final status of the scenario."):
            self._asserterror("Scenario", "")

        if self.RESULT("The error is stored with status of the step in error."):
            self._asserterror("Step", "steps[0].executions[0].")

        if self.RESULT("The error is stored with status of the action in error."):
            self._asserterror("Action/result", "steps[0].actions-results[1].executions[0].")

    def _asserterror(
            self,
            obj_type,  # type: str
            json_path_prefix,  # type: str
    ):  # type: (...) -> None
        self.assertjson(
            self.getexecstep(CheckJsonReportExpectations).json, json_path_prefix + "errors",
            type=list, len=1,
            evidence="%s number of errors" % obj_type,
        )
        self.assertjson(
            self.getexecstep(CheckJsonReportExpectations).json, json_path_prefix + "errors[0].type",
            value="AssertionError",
            evidence="%s error type" % obj_type,
        )
        self.assertjson(
            self.getexecstep(CheckJsonReportExpectations).json, json_path_prefix + "errors[0].message",
            value="This is an exception.",
            evidence="%s error message" % obj_type,
        )
        self.assertjson(
            self.getexecstep(CheckJsonReportExpectations).json, json_path_prefix + "errors[0].location",
            value=FailingScenario001.getinstance().error_location.tolongstring(),
            evidence="%s error location" % obj_type,
        )
