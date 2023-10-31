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


class Issue003(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckScenarioLogExpectations, CheckScenarioReportExpectations, ExecScenario, ParseScenarioLog

        scenario.test.TestCase.__init__(
            self,
            title="Issue #3! Actions / Results differenciation even at the same location",
            description=(
                "Check that actions and expected resulted are differenciated even if they have the same location, "
                "especially in scenario reports."
            ),
        )
        self.verifies(
            scenario.test.reqs.SCENARIO_EXECUTION,
            scenario.test.reqs.SCENARIO_LOGGING,
            scenario.test.reqs.SCENARIO_REPORT,
        )

        # Scenario expectations.
        self.addstep(ExecScenario(
            scenario.test.paths.ACTION_RESULT_LOOP_SCENARIO, generate_report=True,
        ))

        # Scenario expectations.
        _scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.ACTION_RESULT_LOOP_SCENARIO,
            steps=True, actions_results=True,
        )  # type: scenario.test.ScenarioExpectations

        # Verifications.
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), _scenario_expectations))
        self.addstep(CheckScenarioReportExpectations(ExecScenario.getinstance(), _scenario_expectations))
