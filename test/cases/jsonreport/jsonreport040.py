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


class JsonReport040(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from jsonreport.steps.full import CheckFullJsonReport
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="JSON report subscenario",
            objective="Check the JSON report is generated as expected for a super scenario executing a subscenario.",
            features=[scenario.test.features.SCENARIO_REPORT, scenario.test.features.SUBSCENARIOS],
        )

        self.addstep(ExecScenario(scenario.test.paths.SUPERSCENARIO_SCENARIO, generate_report=True))
        self.addstep(CheckFullJsonReport(ExecScenario.getinstance()))
