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


class ConfigDb020(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        from configdb.steps.subprocesslog import CheckConfigValueScenarioLog
        from steps.common import ExecScenario

        scenario.test.TestCase.__init__(
            self,
            title="Configuration value from code",
            description="Check that a configuration value can be set from the code.",
        )
        self.covers(
            scenario.test.reqs.CONFIG_DB,
        )

        self.addstep(ExecScenario(scenario.test.paths.CONFIG_DB_SCENARIO))
        self.addstep(CheckConfigValueScenarioLog(
            ExecScenario.getinstance(),
            key="foo.bar",
            origin=scenario.CodeLocation(
                scenario.test.paths.CONFIG_DB_SCENARIO,
                35,  # location: CONFIG_DB_SCENARIO/set
                "ConfigDbScenario.step000",
            ).tolongstring(),
            value="1",
        ))
