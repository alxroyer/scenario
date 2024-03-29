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
from steps.common import ExecScenario
from jsonreport.steps.full import CheckFullJsonReport


class DocOnly002(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="--doc-only JSON report",
            objective="Check the JSON report for a --doc-only execution.",
            features=[scenario.test.features.DOC_ONLY, scenario.test.features.SCENARIO_REPORT],
        )

        self.addstep(ExecScenario(scenario.test.paths.FAILING_SCENARIO, doc_only=True, generate_report=True))
        self.addstep(CheckFullJsonReport(ExecScenario.getinstance()))
