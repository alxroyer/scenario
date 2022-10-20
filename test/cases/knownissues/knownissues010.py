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


class KnownIssues010(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Known issues - relax mode",
            objective="Check known issues generate warnings in relax mode, and that the status of the test is WARNINGS.",
            features=[scenario.test.features.KNOWN_ISSUES],
        )

        self.addstep(ExecScenario(scenario.test.paths.KNOWN_ISSUES_SCENARIO))
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUES_SCENARIO,
            # Check all steps are executed.
            steps=True, stats=True,
            # Error details makes the step check the warnings, i.e. known issues.
            error_details=True,
        )))
