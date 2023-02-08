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
from campaigns.steps.execution import ExecCampaign
from .knownissues210 import CheckNamedIssueLevel
# Related scenarios:
from knownissuedetailsscenario import KnownIssueDetailsScenario


class KnownIssues290(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Issue level names & campaigns",
            objective="Check that issue level names are displayed in campaign logs and in final results.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.CAMPAIGNS],
        )

        self.addstep(ExecCampaign(
            [scenario.test.paths.TEST_DATA_TEST_SUITE],
            config_values={
                f"{scenario.ConfigKey.ISSUE_LEVEL_NAMES}.foo": 10,
                KnownIssueDetailsScenario.ConfigKey.LEVEL: 10,
            },
        ))
        self.addstep(CheckNamedIssueLevel(ExecCampaign.getinstance(), name="foo", value=10, count=2))
