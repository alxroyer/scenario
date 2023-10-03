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
        from campaigns.steps.jsonreports import CheckCampaignJsonReports
        from campaigns.steps.junitreport import CheckCampaignJunitReport
        from campaigns.steps.log import CheckCampaignLogExpectations
        from campaigns.steps.outdirfiles import CheckCampaignOutdirFiles
        from campaigns.steps.reqdbfile import CheckCampaignReqdbFile
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
        self.covers(
            scenario.ReqLink(scenario.test.reqs.CAMPAIGNS, comments="Single test suite"),
            scenario.ReqLink(scenario.test.reqs.MULTIPLE_SCENARIO_EXECUTION, comments="Campaign final results"),
            scenario.ReqLink(scenario.test.reqs.SCENARIO_LOGGING, comments="Scenario log files gathered with campaign reports"),
            scenario.ReqLink(scenario.test.reqs.LOGGING_FILE, comments="Scenario log files gathered with campaign reports"),
            scenario.ReqLink(scenario.test.reqs.SCENARIO_REPORT, comments="Scenario reports gathered with campaign reports"),
            scenario.ReqLink(scenario.test.reqs.STATISTICS, comments="Statistics by scenario, integrated for the campaign"),
            scenario.ReqLink(scenario.test.reqs.REQUIREMENT_MANAGEMENT, comments="Requirements in campaign reports"),
            # Note:
            #  TEST_DATA_TEST_SUITE embeds FAILING_SCENARIO,
            #  which makes this test cover ERROR_HANDLING.
            scenario.ReqLink(scenario.test.reqs.ERROR_HANDLING, comments="A scenario error is tracked and does not break the campaign"),
            # Note:
            #  TEST_DATA_TEST_SUITE embeds KNOWN_ISSUE_DETAILS_SCENARIO and KNOWN_ISSUES_SCENARIO,
            #  which makes this test cover KNOWN_ISSUES.
            scenario.ReqLink(scenario.test.reqs.KNOWN_ISSUES, comments="Known issues reported from scenario to campaign reports"),
        )
        self.checkstepreqcoverage(True)

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
        self.addstep(CheckCampaignLogExpectations(ExecCampaign.getinstance(), _campaign_expectations)).covers(
            # Campaign log...
            self.getreqlinks(scenario.test.reqs.CAMPAIGNS_LOGGING),
            # with errors and known issues.
            self.getreqlinks(scenario.test.reqs.ERROR_HANDLING),
            self.getreqlinks(scenario.test.reqs.KNOWN_ISSUES),
        )
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), _campaign_expectations.all_test_case_expectations)).covers(
            # Campaign final results...
            self.getreqlinks(scenario.test.reqs.CAMPAIGNS_LOGGING),
            # with statistics, errors and known issues.
            self.getreqlinks(scenario.test.reqs.STATISTICS),
            self.getreqlinks(scenario.test.reqs.ERROR_HANDLING),
            self.getreqlinks(scenario.test.reqs.KNOWN_ISSUES),
        )

        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(), _campaign_expectations)).covers(
            # Campaign outputs...
            self.getreqlinks(scenario.test.reqs.CAMPAIGNS_LOGGING),
            # with requirements...
            self.getreqlinks(scenario.test.reqs.REQUIREMENT_MANAGEMENT),
            # and log and scenario report files.
            self.getreqlinks(scenario.test.reqs.LOGGING_FILE),
            self.getreqlinks(scenario.test.reqs.SCENARIO_REPORT),
        )
        self.knownissue(
            level=scenario.test.IssueLevel.TEST, id="#83",
            message="Step missing to check LOGGING/File and SCENARIO_LOGGING requirements",
        )
        # self.addstep(CheckCampaignLogReports(ExecCampaign.getinstance(), _campaign_expectations)).covers(
        #     # Content of scenario log files...
        #     self.getreqlinks(scenario.test.reqs.CAMPAIGNS_FINAL_RESULTS),
        #     self.getreqlinks(scenario.test.reqs.SCENARIO_LOGGING), self.reqid2links(scenario.test.reqs.LOGGING_FILE),
        #     # with statistics, errors and known issues.
        #     self.getreqlinks(scenario.test.reqs.STATISTICS),
        #     self.getreqlinks(scenario.test.reqs.ERROR_HANDLING),
        #     self.getreqlinks(scenario.test.reqs.KNOWN_ISSUES),
        # )
        self.addstep(CheckCampaignJsonReports(ExecCampaign.getinstance(), _campaign_expectations)).covers(
            # Content of scenario reports...
            self.getreqlinks(scenario.test.reqs.CAMPAIGNS_REPORTS),
            self.getreqlinks(scenario.test.reqs.SCENARIO_REPORT),
            # with statistics, errors and known issues.
            self.getreqlinks(scenario.test.reqs.STATISTICS),
            self.getreqlinks(scenario.test.reqs.ERROR_HANDLING),
            self.getreqlinks(scenario.test.reqs.KNOWN_ISSUES),
        )
        self.addstep(CheckCampaignJunitReport(ExecCampaign.getinstance(), _campaign_expectations)).covers(
            # Campaign report...
            self.getreqlinks(scenario.test.reqs.CAMPAIGNS_REPORTS),
            # with statistics, errors and known issues.
            self.getreqlinks(scenario.test.reqs.STATISTICS),
            self.getreqlinks(scenario.test.reqs.ERROR_HANDLING),
            self.getreqlinks(scenario.test.reqs.KNOWN_ISSUES),
        )
        self.addstep(CheckCampaignReqdbFile(ExecCampaign.getinstance(), _campaign_expectations)).covers(
            self.getreqlinks(scenario.test.reqs.REQUIREMENT_MANAGEMENT)
        )
