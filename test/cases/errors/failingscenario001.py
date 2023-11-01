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

import pathlib

import scenario
import scenario.test

if True:
    from steps.common import LogVerificationStep as _LogVerificationStepImpl  # `LogVerificationStep` used for inheritance.


class FailingScenario001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckScenarioLogExpectations, CheckScenarioReportExpectations, ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Failing scenario execution",
            description=(
                "Check a scenario ends in error as soon as an exception is thrown. "
                "Check the error is displayed and stored appropriately."
            ),
        )
        self.expectstepreqrefinement(True).verifies(
            # Main features:
            scenario.test.reqs.ERROR_HANDLING,
            # Additional coverage:
            (scenario.test.reqs.SCENARIO_LOGGING, "Scenario logging with errors"),
            (scenario.test.reqs.SCENARIO_REPORT, "Scenario report with errors"),
        )

        self.scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.FAILING_SCENARIO,
            # Generate the expectation details about steps, actions and expected results, in order to check how the error affects them.
            steps=True, actions_results=True,
            # Check details about error info and statistics as well.
            error_details=True, stats=True,
        )  # type: scenario.test.ScenarioExpectations

        self.addstep(ExecScenario(scenario.test.paths.FAILING_SCENARIO, generate_report=True, expected_return_code=scenario.ErrorCode.TEST_ERROR)).verifies(
            scenario.test.reqs.ERROR_HANDLING,
        )
        # Log output.
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), self.scenario_expectations)).verifies(
            scenario.test.reqs.ERROR_HANDLING,
            (scenario.test.reqs.SCENARIO_LOGGING, "Actions & expected results displayed until the error occurs"),
        )
        self.addstep(CheckLogOutputExceptionDisplay(ExecScenario.getinstance())).verifies(
            scenario.test.reqs.ERROR_HANDLING,
            (scenario.test.reqs.SCENARIO_LOGGING, "Traceback displayed"),
        )
        # Scenario report.
        self.knownissue(
            level=scenario.test.IssueLevel.TEST,
            message="CheckScenarioReportExpectations should check all steps, actions & expected results definitions, even after failure",
        )
        self.addstep(CheckScenarioReportExpectations(ExecScenario.getinstance(), self.scenario_expectations)).verifies(
            scenario.test.reqs.ERROR_HANDLING,
            (scenario.test.reqs.SCENARIO_REPORT, "All actions & expected results definitions saved, executed until the error occurs"),
        )
        self.addstep(CheckScenarioReportExceptionStorage(CheckScenarioReportExpectations.getinstance())).verifies(
            scenario.test.reqs.ERROR_HANDLING,
            (scenario.test.reqs.SCENARIO_REPORT, "Error storage at each level: scenario, step, action & expected result"),
        )

    @property
    def error_location(self):  # type: () -> scenario.CodeLocation
        assert self.scenario_expectations.errors and (len(self.scenario_expectations.errors) == 1)
        assert self.scenario_expectations.errors[0].location
        return scenario.CodeLocation.fromlongstring(self.scenario_expectations.errors[0].location)


class CheckLogOutputExceptionDisplay(_LogVerificationStepImpl):

    def step(self):  # type: (...) -> None
        self.STEP("Log output error display")

        if self.RESULT("The exception info is displayed twice."):
            self.assertlinecount(
                "AssertionError: This is an exception.", 2,
                evidence="Error type",
            )
        if self.RESULT("The error location is displayed twice by the way, as regular traceback lines."):
            _error_location = (
                # Use a `pathlib.Path` object in order to ensure a path display consistent with the current environment:
                f"File \"{pathlib.Path(scenario.test.paths.FAILING_SCENARIO)}\", "
                f"line {FailingScenario001.getinstance().error_location.line}, "
                f"in {FailingScenario001.getinstance().error_location.qualname}"
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


class CheckScenarioReportExceptionStorage(scenario.test.VerificationStep):

    def step(self):  # type: (...) -> None
        self.STEP("Scenario report error storage")

        if self.RESULT("The error is stored with the final status of the scenario."):
            self._asserterror("scenario", "")

        if self.RESULT("The error is stored with status of the step in error."):
            self._asserterror("step", "steps[0].executions[0].")

        if self.RESULT("The error is stored with status of the action in error."):
            self._asserterror("action/result", "steps[0].actions-results[1].executions[0].")

    def _asserterror(
            self,
            obj_type,  # type: str
            jsonpath_prefix,  # type: str
    ):  # type: (...) -> None
        from steps.common import CheckScenarioReportExpectations

        self.assertjson(
            self.getexecstep(CheckScenarioReportExpectations).json, f"{jsonpath_prefix}errors",
            type=list, len=1,
            evidence=f"{obj_type.capitalize()} number of errors",
        )
        self.assertjson(
            self.getexecstep(CheckScenarioReportExpectations).json, f"{jsonpath_prefix}errors[0].type",
            value="AssertionError",
            evidence=f"{obj_type.capitalize()} error type",
        )
        self.assertjson(
            self.getexecstep(CheckScenarioReportExpectations).json, f"{jsonpath_prefix}errors[0].message",
            value="This is an exception.",
            evidence=f"{obj_type.capitalize()} error message",
        )
        self.assertjson(
            self.getexecstep(CheckScenarioReportExpectations).json, f"{jsonpath_prefix}errors[0].location",
            value=FailingScenario001.getinstance().error_location.tolongstring(),
            evidence=f"{obj_type.capitalize()} error location",
        )
