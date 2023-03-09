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

import typing

import scenario
import scenario.test

from knownissues.steps.knownissuelevelutils import KnownIssueLevelUtils  # `KnownIssueLevelUtils` used for inheritance.
from steps.common import ExecScenario  # `ExecScenario` used for inheritance.


class KnownIssues180(scenario.test.TestCase, KnownIssueLevelUtils):

    def __init__(self):  # type: (...) -> None
        from knownissues.steps.knownissuelevelutils import CheckFinalResultsAscendingIssueLevelOrder
        from steps.common import CheckFinalResultsLogExpectations, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Known issue levels & multiple scenarios",
            objective="Check that scenario results with known issues of different levels are displayed correctly: "
                      "SUCCESS, then WARNINGS, then FAIL tests, "
                      "WARNINGS and FAIL tests being sorted by ascending issue levels each.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.MULTIPLE_SCENARIO_EXECUTION],
        )

        # Execution step.
        self.addstep(ExecKnownIssueLevelScenarios(
            config_values={
                scenario.ConfigKey.ISSUE_LEVEL_ERROR: self.ISSUE_LEVEL_ERROR,
                scenario.ConfigKey.ISSUE_LEVEL_IGNORED: self.ISSUE_LEVEL_IGNORED,
            },
        ))

        # Expectations.
        _scenario_expectations = self._buildscenarioexpectations(
            scenario_paths=ExecKnownIssueLevelScenarios.getinstance().scenario_paths,
            config_values=ExecKnownIssueLevelScenarios.getinstance().config_values,
        )  # type: typing.Sequence[scenario.test.ScenarioExpectations]

        # Verification steps.
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), _scenario_expectations))
        self.addstep(CheckFinalResultsAscendingIssueLevelOrder(ParseFinalResultsLog.getinstance()))


class ExecKnownIssueLevelScenarios(ExecScenario, KnownIssueLevelUtils):

    def __init__(
            self,
            config_values,  # type: scenario.test.configvalues.ConfigValuesType
    ):  # type: (...) -> None
        ExecScenario.__init__(
            self,
            # Prepare a tmp script path for each issue level.
            scenario_paths=self._mktmppaths(),
            description="Scenario executions with different known issue levels",
            config_values=config_values,
            # Certain issue levels are above the error issue level.
            expected_return_code=scenario.ErrorCode.TEST_ERROR,
        )

    def step(self):  # type: (...) -> None
        # Memo: Description already set.

        self._createscenariofilesactions(
            scenario_paths=self.scenario_paths,
        )

        # Execute `ExecScenario.step()`.
        super().step()
