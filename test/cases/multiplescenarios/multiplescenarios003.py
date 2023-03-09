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

import scenario
import scenario.test


class MultipleScenarios003(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from multiplescenarios.steps.expectations import CheckFinalResultsLogExpectations
        from multiplescenarios.steps.parser import ParseFinalResultsLog
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Multiple scenarios & known issues",
            objective="Check the way known issues are displayed in the final results reporting when executing multiple scenarios.",
            features=[scenario.test.features.MULTIPLE_SCENARIO_EXECUTION, scenario.test.features.KNOWN_ISSUES],
        )

        self.section("Known issues only")
        self.addstep(ExecScenario(
            [scenario.test.paths.KNOWN_ISSUES_SCENARIO, scenario.test.paths.SIMPLE_SCENARIO],
            expected_return_code=scenario.ErrorCode.SUCCESS,
        ))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance(0)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(0), scenario_expectations=[
            scenario.test.data.scenarioexpectations(
                scenario.test.paths.KNOWN_ISSUES_SCENARIO, config_values={scenario.test.data.scenarios.KnownIssuesScenario.ConfigKey.RAISE_EXCEPTIONS: False},
                error_details=True, stats=True,
            ),
            scenario.test.data.scenarioexpectations(scenario.test.paths.SIMPLE_SCENARIO),
        ]))

        self.section("Known issues mixed with errors")
        self.addstep(ExecScenario(
            [scenario.test.paths.KNOWN_ISSUES_SCENARIO, scenario.test.paths.SIMPLE_SCENARIO],
            config_values={scenario.test.data.scenarios.KnownIssuesScenario.ConfigKey.RAISE_EXCEPTIONS: "1"},
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance(1)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(1), scenario_expectations=[
            scenario.test.data.scenarioexpectations(
                scenario.test.paths.KNOWN_ISSUES_SCENARIO, config_values={scenario.test.data.scenarios.KnownIssuesScenario.ConfigKey.RAISE_EXCEPTIONS: True},
                error_details=True, stats=True,
            ),
            scenario.test.data.scenarioexpectations(scenario.test.paths.SIMPLE_SCENARIO),
        ]))
