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
from .steps.execution import ExecCampaign
from .steps.log import CheckCampaignLogExpectations
from steps.common import ParseFinalResultsLog, CheckFinalResultsLogExpectations
from .steps.outdirfiles import CheckCampaignOutdirFiles
from .steps.jsonreports import CheckCampaignJsonReports
from .steps.junitreport import CheckCampaignJunitReport


class Campaign002(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Campaign execution with several test suites",
            objective="Check that the campaign runner can execute several test suite files.",
            features=[scenario.test.features.CAMPAIGNS],
        )

        # Campaign execution.
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE, scenario.test.paths.DEMO_TEST_SUITE]))

        # Campaign expectations.
        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(_campaign_expectations, scenario.test.paths.TEST_DATA_TEST_SUITE)
        scenario.test.data.testsuiteexpectations(_campaign_expectations, scenario.test.paths.DEMO_TEST_SUITE)
        assert _campaign_expectations.all_test_case_expectations

        # Verifications.
        self.addstep(CheckCampaignLogExpectations(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), _campaign_expectations.all_test_case_expectations))
        # Check report files for several test suites by the way.
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(CheckCampaignJsonReports(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(CheckCampaignJunitReport(ExecCampaign.getinstance(), _campaign_expectations))
