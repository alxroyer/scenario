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


class Campaign004(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign
        from steps.common import CheckFinalResultsLogExpectations, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Campaign & extra info",
            description="Check extra info display with campaign results.",
        )
        self.covers(
            scenario.test.reqs.CAMPAIGNS,
            scenario.ReqLink(scenario.test.reqs.ATTRIBUTES, comments="Display with campaign final results"),
        )

        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(_campaign_expectations, scenario.test.paths.TEST_DATA_TEST_SUITE, attributes=True)
        assert _campaign_expectations.all_test_case_expectations

        self.section("No extra info")
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE], config_values={scenario.ConfigKey.RESULTS_EXTRA_INFO: ""}))
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance(0)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(0), _campaign_expectations.all_test_case_expectations))

        self.section("Extra info = 'TITLE'")
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE], config_values={scenario.ConfigKey.RESULTS_EXTRA_INFO: "TITLE"}))
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance(1)))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(1), _campaign_expectations.all_test_case_expectations))
