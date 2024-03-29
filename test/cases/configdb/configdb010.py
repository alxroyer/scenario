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

# Steps:
from steps.common import ExecScenario
from .steps.subprocesslog import CheckConfigValueScenarioLog


class ConfigDb010(scenario.test.TestCase):

    def __init__(self):  # type: (...) -> None
        scenario.test.TestCase.__init__(
            self,
            title="Configuration value from command line",
            objective="Check that a configuration value can be set from the command line.",
            features=[scenario.test.features.CONFIG_DB],
        )

        self.addstep(ExecScenario(scenario.test.paths.CONFIG_DB_SCENARIO, config_values={"test_value": 100}))
        self.addstep(CheckConfigValueScenarioLog(
            ExecScenario.getinstance(),
            key="test_value",
            origin="<args>",
            value="'100'",
        ))
