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
from .steps.full import CheckFullJsonReport


class JsonReport041(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="JSON report sub-scenario --doc-only",
            objective="Check the JSON report is generated as expected for a super scenario executing a sub-scenario with the --doc-only option set.",
            features=[scenario.test.features.SCENARIO_REPORT, scenario.test.features.SUBSCENARIOS, scenario.test.features.DOC_ONLY],
        )

        self.addstep(ExecScenario(scenario.test.paths.SUPERSCENARIO_SCENARIO, generate_report=True, doc_only=True))
        self.addstep(CheckFullJsonReport(ExecScenario.getinstance()))
