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

import scenario
import scenario.test


class Campaign006(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign
        from campaigns.steps.outdirfiles import CheckCampaignOutdirFiles
        from campaigns.steps.reqdbfile import CheckCampaignReqdbFile

        scenario.test.TestCase.__init__(
            self,
            title="Campaign & requirement file",
            description="Check requirement file output with campaign results.",
        )
        self.covers(
            scenario.test.reqs.CAMPAIGNS,
            (scenario.test.reqs.REQUIREMENT_MANAGEMENT, "Requirement output file management with campaigns"),
        )

        self.section("Tests without requirements, no input requirement file")
        _1 = self.addstep(ExecCampaign([scenario.test.paths.DEMO_TEST_SUITE]))
        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        _campaign_expectations.reqdbfile(False)
        self.addstep(CheckCampaignOutdirFiles(_1, _campaign_expectations))

        self.section("Tests without requirements, input requirement file")
        _2 = self.addstep(ExecCampaign([scenario.test.paths.DEMO_TEST_SUITE], config_values={
            scenario.ConfigKey.REQDB_FILES: scenario.test.paths.REQDB_FILE,
        }))
        _campaign_expectations = scenario.test.CampaignExpectations()  # Type already declared above.
        _campaign_expectations.reqdbfile(scenario.test.paths.REQDB_FILE, titles_and_texts=True)
        self.addstep(CheckCampaignOutdirFiles(_2, _campaign_expectations))
        self.addstep(CheckCampaignReqdbFile(_2, _campaign_expectations))

        self.section("Tests with requirements, no input requirement file")
        _3 = self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE]))
        _campaign_expectations = scenario.test.CampaignExpectations()  # Type already declared above.
        _campaign_expectations.reqdbfile(scenario.test.paths.REQDB_FILE, titles_and_texts=False)
        self.addstep(CheckCampaignOutdirFiles(_3, _campaign_expectations))
        self.addstep(CheckCampaignReqdbFile(_3, _campaign_expectations))

        self.section("Tests with requirements, input requirement file")
        _4 = self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE], config_values={
            scenario.ConfigKey.REQDB_FILES: scenario.test.paths.REQDB_FILE,
        }))
        _campaign_expectations = scenario.test.CampaignExpectations()  # Type already declared above.
        _campaign_expectations.reqdbfile(scenario.test.paths.REQDB_FILE, titles_and_texts=True)
        self.addstep(CheckCampaignOutdirFiles(_4, _campaign_expectations))
        self.addstep(CheckCampaignReqdbFile(_4, _campaign_expectations))
