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

# Steps:
from .steps.execution import ExecScenario
from steps.common import ParseScenarioLog, CheckScenarioLogExpectations


class Inheritance001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Inheritance & step order",
            objective="Check step order when a scenario inherits from another one.",
            features=[scenario.test.features.ALTERNATIVE_SCENARIOS, scenario.test.features.SCENARIO_EXECUTION],
        )

        self.addstep(ExecScenario(scenario.test.paths.INHERITING_SCENARIO))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), scenario.test.data.scenarioexpectations(
            scenario.test.paths.INHERITING_SCENARIO,
            # Check step order in the log output.
            steps=True,
        )))
