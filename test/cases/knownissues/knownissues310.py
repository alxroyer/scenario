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
from steps.common import ParseScenarioLog, CheckScenarioLogExpectations
from steps.common import CheckJsonReportExpectations
# Related scenarios:
from knownissuedetailsscenario import KnownIssueDetailsScenario


class KnownIssues310(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Known issue ids",
            objective="Check that known issue identifiers are displayed in the console and saved in scenario reports.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.SCENARIO_LOGGING, scenario.test.features.SCENARIO_REPORT],
        )

        # Execution step.
        self.addstep(ExecScenario(
            scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO,
            config_values={
                KnownIssueDetailsScenario.ConfigKey.ID: "#10",
            },
            generate_report=True,
        ))

        # Expectations.
        _scenario_expectations = scenario.test.data.scenarioexpectations(
            scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO,
            config_values=ExecScenario.getinstance().config_values,
            error_details=True,
        )  # type: scenario.test.ScenarioExpectations
        self.assertequal(self.assertisnotnone(_scenario_expectations.warnings)[0].id, "#10")

        # Verification steps.
        self.addstep(ParseScenarioLog(ExecScenario.getinstance()))
        self.addstep(CheckScenarioLogExpectations(ParseScenarioLog.getinstance(), _scenario_expectations))
        self.addstep(CheckJsonReportExpectations(ExecScenario.getinstance(), _scenario_expectations))
