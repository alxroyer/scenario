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

import scenario
import scenario.test
import scenario.text

# Steps:
from steps.common import ExecScenario
from steps.common import LogVerificationStep
# Related scenarios:
from knownissuedetailsscenario import KnownIssueDetailsScenario


class KnownIssues210(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Issue level names",
            objective="Check that issue levels can be configured with meaningful names, and that these names are displayed in the console.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.SCENARIO_LOGGING],
        )

        self.addstep(ExecScenario(
            scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO,
            config_values={
                f"{scenario.ConfigKey.ISSUE_LEVEL_NAMES}.foo": 10,
                KnownIssueDetailsScenario.ConfigKey.LEVEL: 10,
            },
        ))
        self.addstep(CheckNamedIssueLevel(ExecScenario.getinstance(), name="foo", value=10, count=2))


class CheckNamedIssueLevel(LogVerificationStep):

    def __init__(
            self,
            exec_step,  # type: scenario.test.AnyExecutionStepType
            name,  # type: str
            value,  # type: int
            count,  # type: int
    ):  # type: (...) -> None
        LogVerificationStep.__init__(self, exec_step)

        self.issue_level_name = name  # type: str
        self.issue_level_value = value  # type: int
        self.count = count  # type: int

    def step(self):  # type: (...) -> None
        self.STEP(f"Named issue level")

        if self.RESULT(f"The known issue is displayed {scenario.text.adverbial(self.count)} with the name attached to its issue level."):
            self.assertlinecount(
                f"Issue({self.issue_level_name}={self.issue_level_value})!", self.count,
                evidence=True,
            )
