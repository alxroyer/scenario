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


class Campaign001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Campaign execution reports",
            objective=(
                "Check that the campaign runner can execute a test suite file, "
                "gather the test case log files and reports, "
                "and produce the campaign report. "
                "Check furthermore that error display makes it easy to investigate on errors and warnings."
            ),
            features=[scenario.test.features.CAMPAIGNS, scenario.test.features.ERROR_HANDLING, scenario.test.features.KNOWN_ISSUES],
        )

        # Campaign execution.
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE]))

        # Campaign expectations.
        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        # Note: TEST_DATA_TEST_SUITE embeds the FAILING_SCENARIO, which makes the steps below test ERROR_HANDLING.
        #       let's activate the `error_details` option for the purpose.
        scenario.test.data.testsuiteexpectations(_campaign_expectations, scenario.test.paths.TEST_DATA_TEST_SUITE, error_details=True, stats=True)
        assert _campaign_expectations.all_test_case_expectations

        # Verifications.
        self.addstep(CheckCampaignLogExpectations(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), _campaign_expectations.all_test_case_expectations))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(CheckCampaignJsonReports(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(CheckCampaignJunitReport(ExecCampaign.getinstance(), _campaign_expectations))
