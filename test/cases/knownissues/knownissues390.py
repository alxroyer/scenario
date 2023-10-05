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

import typing

import scenario.test


class KnownIssues390(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign
        from campaigns.steps.log import CheckCampaignLogExpectations
        from steps.common import CheckFinalResultsLogExpectations, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Known issue ids & campaigns",
            description="Check that known issue identifiers are displayed in the campaign log and in final results.",
        )
        self.verifies(
            scenario.test.reqs.KNOWN_ISSUES,
            scenario.test.reqs.CAMPAIGNS,
        )

        # Execution step.
        self.addstep(ExecCampaign(
            [scenario.test.paths.TEST_DATA_TEST_SUITE],
            config_values={
                scenario.test.data.scenarios.KnownIssueDetailsScenario.ConfigKey.ID: "#10",
            },
        ))

        # Scenario expectations.
        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(
            _campaign_expectations,
            scenario.test.paths.TEST_DATA_TEST_SUITE,
            config_values=ExecCampaign.getinstance().config_values,
            error_details=True,
        )
        _id_expectation = None  # type: typing.Any
        for _scenario_expectations in self.assertisnotnone(_campaign_expectations.all_test_case_expectations):  # type: scenario.test.ScenarioExpectations
            if _scenario_expectations.script_path == scenario.test.paths.KNOWN_ISSUE_DETAILS_SCENARIO:
                self.assertlen(_scenario_expectations.warnings, 1)
                _id_expectation = self.assertisnotnone(_scenario_expectations.warnings)[0].id
        self.assertequal(_id_expectation, "#10")

        # Verification steps.
        self.addstep(CheckCampaignLogExpectations(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(
            ParseFinalResultsLog.getinstance(),
            self.assertisnotnone(_campaign_expectations.all_test_case_expectations),
        ))
