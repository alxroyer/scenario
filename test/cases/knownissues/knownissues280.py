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


class KnownIssues280(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from knownissues.knownissues210 import CheckNamedIssueLevel
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Issue level names & multiple scenarios",
            description="Check that issue level names are displayed in the console in multiple scenario results.",
        )
        self.covers(
            scenario.test.reqs.KNOWN_ISSUES,
            scenario.test.reqs.MULTIPLE_SCENARIO_EXECUTION,
        )

        self.addstep(ExecScenario(
            [scenario.test.paths.SIMPLE_SCENARIO, scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO],
            config_values={
                f"{scenario.ConfigKey.ISSUE_LEVEL_NAMES}.foo": 10,
                scenario.test.data.scenarios.KnownIssueDetailsScenario.ConfigKey.LEVEL: 10,
            },
        ))
        self.addstep(CheckNamedIssueLevel(ExecScenario.getinstance(), name="foo", value=10, count=3))
