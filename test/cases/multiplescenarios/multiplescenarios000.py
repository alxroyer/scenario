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

import typing

import scenario
import scenario.test

if True:
    from steps.common import LogVerificationStep as _LogVerificationStepImpl  # `LogVerificationStep` used for inheritance.
if typing.TYPE_CHECKING:
    from steps.common import ExecScenario as _ExecScenarioType


class MultipleScenarios000(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckFinalResultsLogExpectations, ExecScenario, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Multiple scenarios & incompatible options",
            description="Check that a couple of options are incompatible with multiple scenario executions.",
            features=[scenario.test.features.MULTIPLE_SCENARIO_EXECUTION],
        )

        self.section("Successful execution")
        self.addstep(ExecScenario(
            [scenario.test.paths.FAILING_SCENARIO, scenario.test.paths.SUPERSCENARIO_SCENARIO],
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance(0)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(0), [
            scenario.test.data.scenarioexpectations(scenario.test.paths.FAILING_SCENARIO),
            scenario.test.data.scenarioexpectations(scenario.test.paths.SUPERSCENARIO_SCENARIO),
        ]))

        self.section("--json-report option")
        self.addstep(ExecScenario(
            [scenario.test.paths.FAILING_SCENARIO, scenario.test.paths.SUPERSCENARIO_SCENARIO],
            generate_report=True,
            expected_return_code=scenario.ErrorCode.ARGUMENTS_ERROR,
        ))
        self.addstep(CheckMultipleScenariosIncompatibleOption(ExecScenario.getinstance(1), option="--json-report"))


class CheckMultipleScenariosIncompatibleOption(_LogVerificationStepImpl):

    def __init__(
            self,
            exec_step,  # type: _ExecScenarioType
            option,  # type: str
    ):  # type: (...) -> None
        _LogVerificationStepImpl.__init__(self, exec_step)

        self.option = option  # type: str

    def step(self):  # type: (...) -> None
        self.STEP(f"No {self.option} option")

        if self.RESULT("The log output is less than 10 lines."):
            self.assertlessequal(
                len(self.subprocess.stdout.splitlines()), 10,
                evidence="Number of lines",
            )

        if self.RESULT(f"The scenario launcher displayed an error message regarding the {self.option} option."):
            self.assertline(
                f"Cannot use the {self.option} option with multiple scenario files",
                evidence="Error message",
            )
