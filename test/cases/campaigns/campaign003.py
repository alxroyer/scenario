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
from .steps.dtoutdir import CheckCampaignDtOutdir, CheckCampaignNoDtOutdir
from .steps.outdirfiles import CheckCampaignOutdirFiles


class Campaign003(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Campaign --dt-subdir option",
            objective="Check the creation of date/time subdirectory for campaign results when the --dt-subdir option is used.",
            features=[scenario.test.features.CAMPAIGNS],
        )

        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(_campaign_expectations, scenario.test.paths.TEST_DATA_TEST_SUITE)

        self.section("--dt-subdir option not set")
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE], dt_subdir=False))
        self.addstep(CheckCampaignNoDtOutdir(ExecCampaign.getinstance(0)))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(0), _campaign_expectations))

        self.section("--dt-subdir option set")
        self.addstep(ExecCampaign([scenario.test.paths.TEST_DATA_TEST_SUITE], dt_subdir=True))
        self.addstep(CheckCampaignDtOutdir(ExecCampaign.getinstance(1)))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(1), _campaign_expectations))
