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


class Campaign005(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign
        from steps.common import CheckFinalResultsLogExpectations, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Campaign & extra info",
            description="Check extra info display with campaign results.",
        )
        self.verifies(
            (scenario.test.reqs.CAMPAIGN_LOGGING, ),
            (scenario.test.reqs.ATTRIBUTES, "Display with campaign final results"),
        )

        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(_campaign_expectations, scenario.test.paths.TEST_DATA_TEST_SUITE, attributes=True)
        assert _campaign_expectations.all_test_case_expectations

        self.section("No extra info")
        _e1 = self.addstep(ExecCampaign(
            [scenario.test.paths.TEST_DATA_TEST_SUITE],
            config_values={scenario.ConfigKey.RESULTS_EXTRA_INFO: ""},
        ))
        _p1 = self.addstep(ParseFinalResultsLog(_e1))
        self.addstep(CheckFinalResultsLogExpectations(_p1, _campaign_expectations.all_test_case_expectations))

        self.section("Extra info = TITLE")
        _e2 = self.addstep(ExecCampaign(
            [scenario.test.paths.TEST_DATA_TEST_SUITE],
            config_values={scenario.ConfigKey.RESULTS_EXTRA_INFO: "TITLE"},
        ))
        _p2 = self.addstep(ParseFinalResultsLog(_e2))
        self.addstep(CheckFinalResultsLogExpectations(_p2, _campaign_expectations.all_test_case_expectations))

        self.section("Extra info = TITLE and DESCRIPTION")
        _e3 = self.addstep(ExecCampaign(
            [scenario.test.paths.TEST_DATA_TEST_SUITE],
            config_values={scenario.ConfigKey.RESULTS_EXTRA_INFO: "TITLE, DESCRIPTION"},
        ))
        _p3 = self.addstep(ParseFinalResultsLog(_e3))
        self.addstep(CheckFinalResultsLogExpectations(_p3, _campaign_expectations.all_test_case_expectations))
