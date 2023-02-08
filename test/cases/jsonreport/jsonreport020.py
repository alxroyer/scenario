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

# Steps:
from steps.common import ExecScenario
from .steps.full import CheckFullJsonReport


class JsonReport020(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="JSON report failing scenario",
            objective="Check the JSON report is generated as expected for a failing scenario.",
            features=[scenario.test.features.SCENARIO_REPORT, scenario.test.features.ERROR_HANDLING],
        )

        self.addstep(ExecScenario(scenario.test.paths.FAILING_SCENARIO, expected_return_code=scenario.ErrorCode.TEST_ERROR, generate_report=True))
        self.addstep(CheckFullJsonReport(ExecScenario.getinstance()))
