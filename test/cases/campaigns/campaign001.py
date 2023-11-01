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


class Campaign001(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign
        from campaigns.steps.junitreport import CheckCampaignJunitReport
        from campaigns.steps.log import CheckCampaignLogExpectations
        from campaigns.steps.outdirfiles import CheckCampaignOutdirFiles
        from campaigns.steps.reqdbfile import CheckCampaignReqdbFile
        from campaigns.steps.scenarioreports import CheckCampaignScenarioReports
        from steps.common import CheckFinalResultsLogExpectations, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Campaign execution & reports",
            description=(
                "Check that the campaign runner can execute a test suite file (CAMPAIGNS), "
                "gather the test case log files (LOGGING), reports (SCENARIO_REPORT) and statistics (STATISTICS), "
                "and produce the campaign report (CAMPAIGNS) and requirement file (REQUIREMENT_MANAGEMENT). "
                "Check furthermore that error display makes it easy to investigate on errors and warnings "
                "(MULTIPLE_SCENARIO_EXECUTION, ERROR_HANDLING & KNOWN_ISSUES)."
            ),
        )
        self.expectstepreqrefinement(True).verifies(
            (scenario.test.reqs.CAMPAIGNS, "Single test suite"),
            (scenario.test.reqs.MULTIPLE_SCENARIO_EXECUTION, "Campaign final results"),
            (scenario.test.reqs.SCENARIO_LOGGING, "Scenario log files gathered with campaign reports"),
            (scenario.test.reqs.LOGGING_FILE, "Scenario log files gathered with campaign reports"),
            (scenario.test.reqs.SCENARIO_REPORT, "Scenario reports gathered with campaign reports"),
            (scenario.test.reqs.STATISTICS, "Statistics by scenario, integrated for the campaign"),
            (scenario.test.reqs.REQUIREMENT_MANAGEMENT, "Requirements in campaign reports"),
            # Note:
            #  TEST_DATA_TEST_SUITE embeds FAILING_SCENARIO,
            #  which makes this test cover ERROR_HANDLING.
            (scenario.test.reqs.ERROR_HANDLING, "A scenario error is tracked and does not break the campaign"),
            # Note:
            #  TEST_DATA_TEST_SUITE embeds KNOWN_ISSUE_DETAILS_SCENARIO and KNOWN_ISSUES_SCENARIO,
            #  which makes this test cover KNOWN_ISSUES.
            (scenario.test.reqs.KNOWN_ISSUES, "Known issues reported from scenario to campaign reports")
        )

        # Campaign execution.
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE]))

        # Campaign expectations.
        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(
            _campaign_expectations, scenario.test.paths.TEST_DATA_TEST_SUITE,
            # Activate `error_details` and `stats` to cover ERROR_HANDLING, KNOWN_ISSUES and STATISTICS requirements.
            error_details=True, stats=True,
        )
        assert _campaign_expectations.all_test_case_expectations
        _campaign_expectations.reqdbfile(scenario.test.paths.REQDB_FILE)

        # Verifications.
        self.addstep(CheckCampaignLogExpectations(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_LOGGING, "Main campaign logging"),
            (scenario.test.reqs.ERROR_HANDLING, "Scenario errors logged with main campaign logging"),
            (scenario.test.reqs.KNOWN_ISSUES, "Known issues logged with main campaign logging"),
        )
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), _campaign_expectations.all_test_case_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_LOGGING, "Campaign final results"),
            (scenario.test.reqs.STATISTICS, "Statistics logged with campaign final results"),
            (scenario.test.reqs.ERROR_HANDLING, "Scenario errors logged with campaign final results"),
            (scenario.test.reqs.KNOWN_ISSUES, "Known issues logged with campaign final results"),
        )

        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_LOGGING, "Campaign output files"),
            (scenario.test.reqs.REQUIREMENT_MANAGEMENT, "Requirements saved with campaign output files"),
            (scenario.test.reqs.LOGGING_FILE, "Scenario logging saved with campaign output files"),
            (scenario.test.reqs.SCENARIO_REPORT, "Scenario reports saved with campaign output files"),
        )
        self.knownissue(
            level=scenario.test.IssueLevel.TEST, id="#83",
            message="Step missing to check LOGGING/File and SCENARIO_LOGGING requirements",
        )
        # self.addstep(CheckCampaignLogReports(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
        #     # Content of scenario log files...
        #     self.getreqlinks(scenario.test.reqs.CAMPAIGNS_FINAL_RESULTS),
        #     self.getreqlinks(scenario.test.reqs.SCENARIO_LOGGING), self.reqid2links(scenario.test.reqs.LOGGING_FILE),
        #     # with statistics, errors and known issues.
        #     self.getreqlinks(scenario.test.reqs.STATISTICS),
        #     self.getreqlinks(scenario.test.reqs.ERROR_HANDLING),
        #     self.getreqlinks(scenario.test.reqs.KNOWN_ISSUES),
        # )
        self.addstep(CheckCampaignScenarioReports(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_REPORTS, "Scenario report content in campaign output files"),
            (scenario.test.reqs.SCENARIO_REPORT, "Scenario report content in campaign output files"),
            (scenario.test.reqs.STATISTICS, "Statistics saved in scenario reports in campaign output files"),
            (scenario.test.reqs.ERROR_HANDLING, "Scenario errors saved in scenario reports in campaign output files"),
            (scenario.test.reqs.KNOWN_ISSUES, "Known issues saved in scenario reports in campaign output files"),
        )
        self.addstep(CheckCampaignJunitReport(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_REPORTS, "Campaign report content"),
            (scenario.test.reqs.STATISTICS, "Statistics saved in campaign report content"),
            (scenario.test.reqs.ERROR_HANDLING, "Scenario errors saved in campaign report content"),
            (scenario.test.reqs.KNOWN_ISSUES, "Known issues saved in campaign report content"),
        )
        self.addstep(CheckCampaignReqdbFile(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_REPORTS, "Requirement file content in campaign output files"),
            (scenario.test.reqs.REQUIREMENT_MANAGEMENT, "Requirement file content in campaign output files"),
        )
