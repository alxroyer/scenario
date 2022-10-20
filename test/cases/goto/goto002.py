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

import scenario
import scenario.test

# Steps:
from steps.common import ExecScenario
from jsonreport.steps.full import CheckFullJsonReport
from steps.common import CheckJsonReportExpectations


class Goto002(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Goto scenario reports",
            objective="Check scenario report generation for goto scenarios.",
            features=[scenario.test.features.GOTO, scenario.test.features.SCENARIO_REPORT],
        )

        self.section("Documentation generation")
        self.addstep(ExecScenario(scenario.test.paths.GOTO_SCENARIO, generate_report=True, doc_only=True))
        self.addstep(CheckFullJsonReport(ExecScenario.getinstance(0)))
        self.addstep(CheckJsonReportExpectations(ExecScenario.getinstance(0), scenario.test.data.scenarioexpectations(
            scenario.test.paths.GOTO_SCENARIO,
            steps=True, stats=True,  # Check step order and statistics.
            doc_only=True,
        )))

        self.section("Test execution")
        self.addstep(ExecScenario(scenario.test.paths.GOTO_SCENARIO, generate_report=True, doc_only=False))
        self.addstep(CheckFullJsonReport(ExecScenario.getinstance(1)))
        self.addstep(CheckJsonReportExpectations(ExecScenario.getinstance(1), scenario.test.data.scenarioexpectations(
            scenario.test.paths.GOTO_SCENARIO,
            steps=True, stats=True,  # Check step order and statistics.
            doc_only=False,
        )))
