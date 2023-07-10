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


class ConfigDb500(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from configdb.steps.subprocesslog import CheckConfigValueScenarioLog
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Configuration files overloading",
            description=(
                "Check several configuration files can be loaded from the command line. "
                "Check the one loaded in the end overloads the ones loaded before."
            ),
        )
        self.covers(
            scenario.test.reqs.CONFIG_DB,
        )

        self.section("Conf1 then Conf2")
        self.addstep(ExecScenario(scenario.test.paths.CONFIG_DB_SCENARIO, config_files=[
            scenario.test.paths.datapath("conf1.ini"),
            scenario.test.paths.datapath("conf2.ini"),
        ]))
        self.addstep(CheckConfigValueScenarioLog(
            ExecScenario.getinstance(0),
            key="test.value",
            origin=scenario.test.paths.datapath("conf2.ini").prettypath,
            value="'value2'",
        ))

        self.section("Conf2 then Conf1")
        self.addstep(ExecScenario(scenario.test.paths.CONFIG_DB_SCENARIO, config_files=[
            scenario.test.paths.datapath("conf2.ini"),
            scenario.test.paths.datapath("conf1.ini"),
        ]))
        self.addstep(CheckConfigValueScenarioLog(
            ExecScenario.getinstance(1),
            key="test.value",
            origin=scenario.test.paths.datapath("conf1.ini").prettypath,
            value="'value1'",
        ))
