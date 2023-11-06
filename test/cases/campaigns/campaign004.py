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
        from campaigns.steps.campaignreport import CheckCampaignReport
        from campaigns.steps.execution import ExecCampaign
        from campaigns.steps.outdirfiles import CheckCampaignOutdirFiles

        scenario.test.TestCase.__init__(
            self,
            title="Campaign --doc-only option",
            description="Check campaign results when the --doc-only option is used.",
        )
        self.verifies(
            scenario.test.reqs.CAMPAIGNS,
        )

        self.section("--doc-only option not set")
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE], doc_only=False))
        _regular_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(_regular_expectations, scenario.test.paths.TEST_DATA_TEST_SUITE, stats=True, doc_only=False)
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(0), _regular_expectations))
        self.addstep(CheckCampaignReport(ExecCampaign.getinstance(0), _regular_expectations))

        self.section("--doc-only option set")
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE], doc_only=True))
        _doc_only_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(_doc_only_expectations, scenario.test.paths.TEST_DATA_TEST_SUITE, stats=True, doc_only=True)
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(1), _doc_only_expectations))
        self.addstep(CheckCampaignReport(ExecCampaign.getinstance(1), _doc_only_expectations))
