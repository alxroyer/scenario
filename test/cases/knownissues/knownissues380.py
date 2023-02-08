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

import scenario.test

# Steps:
from steps.common import ExecScenario
from steps.common import ParseFinalResultsLog, CheckFinalResultsLogExpectations
# Related scenarios:
from knownissuedetailsscenario import KnownIssueDetailsScenario


class KnownIssues380(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Known issue ids & multiple scenarios",
            objective="Check that known issue identifiers are displayed in the console in multiple scenario results.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.MULTIPLE_SCENARIO_EXECUTION],
        )

        # Execution step.
        self.addstep(ExecScenario(
            [scenario.test.paths.SIMPLE_SCENARIO, scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO],
            config_values={
                KnownIssueDetailsScenario.ConfigKey.ID: "#10",
            },
        ))

        # Scenario expectations.
        _scenario_expectations = [
            scenario.test.data.scenarioexpectations(
                scenario.test.paths.SIMPLE_SCENARIO,
                config_values=ExecScenario.getinstance().config_values,
                error_details=True,
            ),
            scenario.test.data.scenarioexpectations(
                scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO,
                config_values=ExecScenario.getinstance().config_values,
                error_details=True,
            ),
        ]  # type: typing.List[scenario.test.ScenarioExpectations]
        self.assertlen(_scenario_expectations[1].warnings, 1)
        self.assertequal(self.assertisnotnone(_scenario_expectations[1].warnings)[0].id, "#10")

        # Verification steps.
        self.addstep(ParseFinalResultsLog(ExecScenario.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), _scenario_expectations))
