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
        from campaigns.steps.campaignreport import CheckCampaignReport
        from campaigns.steps.execution import ExecCampaign
        from campaigns.steps.log import CheckCampaignLogExpectations
        from campaigns.steps.outdirfiles import CheckCampaignOutdirFiles
        from campaigns.steps.reqdbfile import CheckCampaignReqDbFile
        from campaigns.steps.scenarioreports import CheckCampaignScenarioReports
        from steps.common import CheckFinalResultsLogExpectations, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Campaign execution & reports",
            description=[
                "Check that the campaign runner can execute a test suite file (CAMPAIGNS), "
                "gather the test case log files (LOGGING), reports (SCENARIO_REPORT) and statistics (STATISTICS), "
                "and produce the campaign report (CAMPAIGNS) and requirement file (REQUIREMENT_MANAGEMENT).",

                "Check furthermore that error display makes it easy to investigate on errors and warnings "
                "(MULTIPLE_SCENARIO_EXECUTION, ERROR_HANDLING & KNOWN_ISSUES).",
            ],
        )
        self.expectstepreqrefinement(True).verifies(
            (scenario.test.reqs.CAMPAIGNS, "Single test suite"),
            (scenario.test.reqs.MULTIPLE_SCENARIO_EXECUTION, "Campaign final results"),
            (scenario.test.reqs.SCENARIO_LOGGING, "Scenario log files gathered with campaign reports"),
            (scenario.test.reqs.LOGGING_FILE, "Scenario log files gathered with campaign reports"),
            (scenario.test.reqs.SCENARIO_REPORT, "Scenario reports gathered with campaign reports"),
            (scenario.test.reqs.STATISTICS, "Statistics by scenario, integrated for the campaign"),
            # Note:
            #   TEST_DATA_TEST_SUITE scenarios define the TITLE attribute in general,
            #   and LONG_TEXTS_SCENARIO also defines the DESCRIPTION attribute,
            #   which makes this test cover ATTRIBUTES.
            (scenario.test.reqs.ATTRIBUTES, "Scenario attributes in campaign reports"),
            # Note:
            #  TEST_DATA_TEST_SUITE embeds REQ_SCENARIO1 and REQ_SCENARIO2,
            #  which makes this test cover REQUIREMENT_MANAGEMENT.
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
            # Make the verifications steps below cover:
            # - ATTRIBUTES
            attributes=True,
            # - ERROR_HANDLING and KNOWN_ISSUES
            error_details=True,
            # - STATISTICS
            stats=True,
        )
        assert _campaign_expectations.all_test_case_expectations
        _campaign_expectations.req_db_file.set(True, content=scenario.test.paths.REQ_DB_FILE)
        _campaign_expectations.downstream_traceability.set(True)
        _campaign_expectations.upstream_traceability.set(True)

        # Verifications:
        # - Campaign log output
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

        # - Campaign output files:
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_LOGGING, "Campaign output files"),
            (scenario.test.reqs.REQUIREMENT_MANAGEMENT, "Requirements saved with campaign output files"),
            (scenario.test.reqs.LOGGING_FILE, "Scenario logging saved with campaign output files"),
            (scenario.test.reqs.SCENARIO_REPORT, "Scenario reports saved with campaign output files"),
        )
        #     - Campaign report
        self.addstep(CheckCampaignReport(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_REPORTS, "Campaign report content"),
            (scenario.test.reqs.STATISTICS, "Statistics saved in campaign report content"),
            (scenario.test.reqs.ERROR_HANDLING, "Scenario errors saved in campaign report content"),
            (scenario.test.reqs.KNOWN_ISSUES, "Known issues saved in campaign report content"),
        )
        #     - Scenario logs
        self.knownissue(
            level=scenario.test.IssueLevel.TEST, id="#83",
            message="Step missing to check LOGGING/File and SCENARIO_LOGGING requirements",
        )
        # self.addstep(CheckCampaignLogReports(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
        #     # Content of scenario log files...
        #     self.getreqlinks(scenario.test.reqs.CAMPAIGNS_FINAL_RESULTS),
        #     self.getreqlinks(scenario.test.reqs.SCENARIO_LOGGING), self.reqid2links(scenario.test.reqs.LOGGING_FILE),
        #     (scenario.test.reqs.ATTRIBUTES, "Attributes saved in scenario logs in campaign output files"),
        #     # with statistics, errors and known issues.
        #     self.getreqlinks(scenario.test.reqs.STATISTICS),
        #     self.getreqlinks(scenario.test.reqs.ERROR_HANDLING),
        #     self.getreqlinks(scenario.test.reqs.KNOWN_ISSUES),
        # )
        #     - Scenario reports
        self.addstep(CheckCampaignScenarioReports(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_REPORTS, "Scenario report content in campaign output files"),
            (scenario.test.reqs.SCENARIO_REPORT, "Scenario report content in campaign output files"),
            (scenario.test.reqs.ATTRIBUTES, "Attributes saved in scenario reports in campaign output files"),
            (scenario.test.reqs.STATISTICS, "Statistics saved in scenario reports in campaign output files"),
            (scenario.test.reqs.ERROR_HANDLING, "Scenario errors saved in scenario reports in campaign output files"),
            (scenario.test.reqs.KNOWN_ISSUES, "Known issues saved in scenario reports in campaign output files"),
        )
        #     - Requirement files
        self.addstep(CheckCampaignReqDbFile(ExecCampaign.getinstance(), _campaign_expectations)).verifies(
            (scenario.test.reqs.CAMPAIGN_REPORTS, "Requirement file content in campaign output files"),
            (scenario.test.reqs.REQUIREMENT_MANAGEMENT, "Requirement file content in campaign output files"),
        )
        self.knownissue(
            level=scenario.test.IssueLevel.TEST, id="#83",
            message="Steps missing to check downstream and upstream traceability reports",
        )
