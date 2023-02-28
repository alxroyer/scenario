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


class ConfigDb200(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from configdb.steps.subprocesslog import CheckConfigValueScenarioLog
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Load JSON configuration file",
            objective="Check that a JSON configuration file can be loaded.",
            features=[scenario.test.features.CONFIG_DB],
        )

        _conf_file = scenario.test.paths.datapath("conf.json")  # type: scenario.Path
        self.addstep(ExecScenario(scenario.test.paths.CONFIG_DB_SCENARIO, config_files=[_conf_file]))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="a.b.c1", origin=_conf_file.prettypath, value="55"))
        # Note: 0.05 and not '0.050' as with INI files.
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="a.b.c2", origin=_conf_file.prettypath, value="0.05"))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="x.y[0].z", origin=_conf_file.prettypath, value="100"))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="x.y[1].z", origin=_conf_file.prettypath, value="101"))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="x.y[2].z", origin=_conf_file.prettypath, value="102"))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="x.y[3].z", origin=_conf_file.prettypath, value="103"))
