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
from steps.common import CheckJsonReportExpectations


class SubScenario002(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Sub-scenario --doc-only",
            objective="Check that a super scenario does not execute its sub-scenarios when the --doc-only option is set.",
            features=[scenario.test.features.SUBSCENARIOS, scenario.test.features.DOC_ONLY],
        )

        _scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.SUPERSCENARIO_SCENARIO,
            doc_only=True,
            steps=True, actions_results=True,
        )  # type: scenario.test.ScenarioExpectations

        self.addstep(ExecScenario(scenario.test.paths.SUPERSCENARIO_SCENARIO, generate_report=True, doc_only=True))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), _scenario_expectations))
        self.addstep(CheckJsonReportExpectations(ExecScenario.getinstance(), _scenario_expectations))
