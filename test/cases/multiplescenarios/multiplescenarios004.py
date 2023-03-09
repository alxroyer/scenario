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


class MultipleScenarios004(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from multiplescenarios.steps.expectations import CheckFinalResultsLogExpectations
        from multiplescenarios.steps.parser import ParseFinalResultsLog
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Multiple scenarios & extra info",
            objective="Check extra info display when executing multiple scenarios.",
            features=[
                # Main features:
                scenario.test.features.MULTIPLE_SCENARIO_EXECUTION, scenario.test.features.ATTRIBUTES,
            ],
        )

        self.section("No extra info")
        self.addstep(ExecScenario(
            [scenario.test.paths.SIMPLE_SCENARIO, scenario.test.paths.FAILING_SCENARIO],
            config_values={scenario.ConfigKey.RESULTS_EXTRA_INFO: ""},
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance(0)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(0), scenario_expectations=[
            scenario.test.data.scenarioexpectations(scenario.test.paths.SIMPLE_SCENARIO, attributes=True),
            scenario.test.data.scenarioexpectations(scenario.test.paths.FAILING_SCENARIO, attributes=True),
        ]))

        self.section("Extra info = 'TITLE'")
        self.addstep(ExecScenario(
            [scenario.test.paths.SIMPLE_SCENARIO, scenario.test.paths.FAILING_SCENARIO],
            config_values={scenario.ConfigKey.RESULTS_EXTRA_INFO: "TITLE"},
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        ))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance(1)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(1), scenario_expectations=[
            scenario.test.data.scenarioexpectations(scenario.test.paths.SIMPLE_SCENARIO, attributes=True),
            scenario.test.data.scenarioexpectations(scenario.test.paths.FAILING_SCENARIO, attributes=True),
        ]))
