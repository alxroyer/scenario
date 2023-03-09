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

import scenario
import scenario.test

from campaigns.steps.execution import ExecCampaign  # `ExecCampaign` used for inheritance.
from knownissues.steps.knownissuelevelutils import KnownIssueLevelUtils  # `KnownIssueLevelUtils` used for inheritance.


class KnownIssues190(scenario.test.TestCase, KnownIssueLevelUtils):

    def __init__(self):  # type: (...) -> None
        from campaigns.steps.log import CheckCampaignLogExpectations
        from knownissues.steps.knownissuelevelutils import CheckFinalResultsAscendingIssueLevelOrder
        from steps.common import CheckFinalResultsLogExpectations, ParseFinalResultsLog

        scenario.test.TestCase.__init__(
            self,
            title="Known issue levels & campaigns",
            objective="Check that campaign results with known issues of different levels are displayed correctly: "
                      "SUCCESS, then WARNINGS, then FAIL tests, "
                      "WARNINGS and FAIL tests being sorted by ascending issue levels each.",
            features=[scenario.test.features.KNOWN_ISSUES, scenario.test.features.CAMPAIGNS],
        )

        # Execution step.
        self.addstep(ExecKnownIssueLevelCampaign(
            config_values={
                scenario.ConfigKey.ISSUE_LEVEL_ERROR: self.ISSUE_LEVEL_ERROR,
                scenario.ConfigKey.ISSUE_LEVEL_IGNORED: self.ISSUE_LEVEL_IGNORED,
            },
        ))

        # Scenario expectations.
        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        _test_suite_expectations = _campaign_expectations.addtestsuite(
            ExecKnownIssueLevelCampaign.getinstance().test_suite_paths[0]
        )  # type: scenario.test.TestSuiteExpectations
        _test_suite_expectations.test_case_expectations = list(self._buildscenarioexpectations(
            scenario_paths=ExecKnownIssueLevelCampaign.getinstance().scenario_paths,
            config_values=ExecKnownIssueLevelCampaign.getinstance().config_values,
        ))
        assert _campaign_expectations.all_test_case_expectations

        # Verification steps.
        self.addstep(CheckCampaignLogExpectations(ExecCampaign.getinstance(), _campaign_expectations))
        self.addstep(ParseFinalResultsLog(ExecCampaign.getinstance()))
        self.addstep(CheckFinalResultsLogExpectations(ParseFinalResultsLog.getinstance(), _campaign_expectations.all_test_case_expectations))
        self.addstep(CheckFinalResultsAscendingIssueLevelOrder(ParseFinalResultsLog.getinstance()))


class ExecKnownIssueLevelCampaign(ExecCampaign, KnownIssueLevelUtils):

    def __init__(
            self,
            config_values,  # type: scenario.test.configvalues.ConfigValuesType
    ):  # type: (...) -> None
        ExecCampaign.__init__(
            self,
            # Prepare a tmp path for the test suite file.
            [self.test_case.mktmppath(suffix=".suite")],
            description="Campaign execution with different known issue levels",
            config_values=config_values,
        )

        # Prepare tmp paths for the test case files.
        self.scenario_paths = self._mktmppaths()  # type: typing.Sequence[scenario.Path]

    def step(self):  # type: (...) -> None
        # Memo: Description already set.

        self._createscenariofilesactions(self.scenario_paths)

        _test_suite_path = self.test_suite_paths[0]  # type: scenario.Path
        if self.ACTION(f"Create a {self.test_case.getpathdesc(_test_suite_path)} test suite file "
                       f"referencing the scenario files created just before."):
            _test_suite_path.write_bytes(
                "\n".join([
                    # Compute a relative path for each test case.
                    *[_scenario_path.relative_to(_test_suite_path.parent) for _scenario_path in self.scenario_paths],
                    # Final empty line.
                    "",
                ]).encode("utf-8"),
            )
            self.evidence(f"File {self.test_case.getpathdesc(_test_suite_path)} '{_test_suite_path}' created "
                          f"with content {scenario.debug.saferepr(_test_suite_path.read_bytes())}")

        # Execute `ExecCampaign.step()`.
        super().step()
