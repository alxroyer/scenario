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
from campaigns.steps.execution import ExecCampaign
from campaigns.steps.log import CheckCampaignLogExpectations
from steps.common import ParseFinalResultsLog, CheckFinalResultsLogExpectations


class KnownIssues090(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Known issues & campaigns",
            objective="Check that known issues in campaign results are displayed correctly: SUCCESS, then WARNINGS, then FAIL tests.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.CAMPAIGNS],
        )

        # Execution step.
        self.addstep(ExecCampaign(
            [scenario.test.paths.TEST_DATA_TEST_SUITE],
        ))

        # Scenario expectations.
        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(
            _campaign_expectations,
            scenario.test.paths.TEST_DATA_TEST_SUITE,
            error_details=True,
        )

        # Verification steps.
        self.addstep(CheckCampaignLogExpectations(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(
            ParseFinalResultsLog.getinstance(),
            self.assertisnotnone(_campaign_expectations.all_test_case_expectations),
        ))
