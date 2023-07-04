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


class Issue42(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from steps.common import CheckFinalResultsLogExpectations, ExecScenario, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Issue #42! Bad known issue display on multiple test execution",
            description="Check that known issues are correctly displayed when several tests are executed in a single command line.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.MULTIPLE_SCENARIO_EXECUTION],
        )

        self.addstep(ExecScenario([
            # The problem occured when:
            # 1) known issues are declared at the scenario definition level,
            # 2) the test with known issues is the last one executed.
            scenario.test.paths.SIMPLE_SCENARIO,
            scenario.test.paths.KNOWN_ISSUES_SCENARIO,
        ]))
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), [
            scenario.test.data.scenarioexpectations(scenario.test.paths.SIMPLE_SCENARIO, error_details=True),
            scenario.test.data.scenarioexpectations(scenario.test.paths.KNOWN_ISSUES_SCENARIO, error_details=True),
        ]))
