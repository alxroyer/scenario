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


class SubScenario003(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckScenarioLogExpectations, CheckScenarioReportExpectations, ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Subscenario error",
            description="Check that a super scenario executing a failing subscenario propagates the subscenario error as is.",
        )
        self.verifies(
            scenario.test.reqs.SUBSCENARIOS,
            scenario.test.reqs.ERROR_HANDLING,
        )

        _scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.SUPERSCENARIO_SCENARIO, config_values={
                scenario.test.data.scenarios.SuperScenario.ConfigKey.SUBSCENARIO_PATH: scenario.test.paths.FAILING_SCENARIO,
            },
            error_details=True, steps=True, actions_results=True,
        )  # type: scenario.test.ScenarioExpectations

        self.addstep(ExecScenario(
            scenario.test.paths.SUPERSCENARIO_SCENARIO, subscenario=scenario.test.paths.FAILING_SCENARIO,
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
            generate_report=True,
        ))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), _scenario_expectations))
        self.addstep(CheckScenarioReportExpectations(ExecScenario.getinstance(), _scenario_expectations))
