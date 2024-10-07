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

import scenario.reqs
import scenario.test


class Campaign003(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from campaigns.steps.execution import ExecCampaign
        from campaigns.steps.outdirfiles import CheckCampaignOutdirFiles
        from campaigns.steps.subdir import CheckCampaignSubdirDateTime, CheckCampaignSubdirNone

        scenario.test.TestCase.__init__(
            self,
            title="Campaign --subdir option",
            description="Check the creation of output subdirectory for campaign results "
                        f"depending on the --subdir option and/or '{scenario.ConfigKey.CAMPAIGN_SUBDIR_MODE}' configuration.",
        )
        self.verifies(
            scenario.reqs.CAMPAIGNS,
        )

        _campaign_expectations = scenario.test.CampaignExpectations()  # type: scenario.test.CampaignExpectations
        scenario.test.data.testsuiteexpectations(_campaign_expectations, scenario.test.paths.SCENARIO_TEST_DATA_TEST_SUITE)

        self.section(f"--subdir and '{scenario.ConfigKey.CAMPAIGN_SUBDIR_MODE}' configuration not set")
        self.addstep(ExecCampaign(
            [scenario.test.paths.SCENARIO_TEST_DATA_TEST_SUITE],
            subdir_mode=None,
            config_values={},
        ))
        self.addstep(CheckCampaignSubdirDateTime(ExecCampaign.getinstance(0)))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(0), _campaign_expectations))

        self.section(f"--subdir='{scenario.CampaignArgs.SubdirMode.DATE_TIME}'")
        self.addstep(ExecCampaign(
            [scenario.test.paths.SCENARIO_TEST_DATA_TEST_SUITE],
            subdir_mode=scenario.CampaignArgs.SubdirMode.DATE_TIME,
            config_values={},
        ))
        self.addstep(CheckCampaignSubdirDateTime(ExecCampaign.getinstance(1)))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(1), _campaign_expectations))

        self.section(f"--subdir='{scenario.CampaignArgs.SubdirMode.NONE}'")
        self.addstep(ExecCampaign(
            [scenario.test.paths.SCENARIO_TEST_DATA_TEST_SUITE],
            subdir_mode=scenario.CampaignArgs.SubdirMode.NONE,
            config_values={},
        ))
        self.addstep(CheckCampaignSubdirNone(ExecCampaign.getinstance(2)))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(2), _campaign_expectations))

        self.section(f"{scenario.ConfigKey.CAMPAIGN_SUBDIR_MODE}='{scenario.CampaignArgs.SubdirMode.DATE_TIME}'")
        self.addstep(ExecCampaign(
            [scenario.test.paths.SCENARIO_TEST_DATA_TEST_SUITE],
            subdir_mode=None,
            config_values={scenario.ConfigKey.CAMPAIGN_SUBDIR_MODE: scenario.CampaignArgs.SubdirMode.DATE_TIME},
        ))
        self.addstep(CheckCampaignSubdirDateTime(ExecCampaign.getinstance(3)))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(3), _campaign_expectations))

        self.section(f"{scenario.ConfigKey.CAMPAIGN_SUBDIR_MODE}='{scenario.CampaignArgs.SubdirMode.NONE}'")
        self.addstep(ExecCampaign(
            [scenario.test.paths.SCENARIO_TEST_DATA_TEST_SUITE],
            subdir_mode=None,
            config_values={scenario.ConfigKey.CAMPAIGN_SUBDIR_MODE: scenario.CampaignArgs.SubdirMode.NONE},
        ))
        self.addstep(CheckCampaignSubdirNone(ExecCampaign.getinstance(4)))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(4), _campaign_expectations))

        self.section(f"--subdir='{scenario.CampaignArgs.SubdirMode.NONE}' "
                     f"and {scenario.ConfigKey.CAMPAIGN_SUBDIR_MODE}='{scenario.CampaignArgs.SubdirMode.DATE_TIME}' "
                     f"(program arguments win on configurations)")
        self.addstep(ExecCampaign(
            [scenario.test.paths.SCENARIO_TEST_DATA_TEST_SUITE],
            subdir_mode=scenario.CampaignArgs.SubdirMode.NONE,
            config_values={scenario.ConfigKey.CAMPAIGN_SUBDIR_MODE: scenario.CampaignArgs.SubdirMode.DATE_TIME},
        ))
        self.addstep(CheckCampaignSubdirNone(ExecCampaign.getinstance(5)))
        self.addstep(CheckCampaignOutdirFiles(ExecCampaign.getinstance(5), _campaign_expectations))
