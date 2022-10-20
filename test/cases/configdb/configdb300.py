# -*- coding: utf-8 -*-

# Copyright 2020-2022 Alexis Royer <https://github.com/Alexis-ROYER/scenario>
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

# Steps:
from steps.pippackages import EnsurePipPackage
from steps.common import ExecScenario
from .steps.subprocesslog import CheckConfigValueScenarioLog


class ConfigDb300(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="YAML configuration file",
            objective="Check that a YAML configuration file can be loaded (when 'pyyaml' is installed).",
            features=[scenario.test.features.CONFIG_DB],
        )

        self.addstep(EnsurePipPackage("pyyaml", "yaml", True))
        _conf_file = scenario.test.paths.datapath("conf.yml")  # type: scenario.Path
        self.addstep(ExecScenario(scenario.test.paths.CONFIG_DB_SCENARIO, config_files=[_conf_file]))
        # Note: 55 and not '055' as with INI files.
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="a.b.c1", origin=_conf_file.prettypath, value="55"))
        # Note: 0.05 and not '0.050' as with INI files.
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="a.b.c2", origin=_conf_file.prettypath, value="0.05"))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="x.y[0].z", origin=_conf_file.prettypath, value="200"))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="x.y[1].z", origin=_conf_file.prettypath, value="201"))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="x.y[2].z", origin=_conf_file.prettypath, value="202"))
        self.addstep(CheckConfigValueScenarioLog(ExecScenario.getinstance(), key="x.y[3].z", origin=_conf_file.prettypath, value="203"))
