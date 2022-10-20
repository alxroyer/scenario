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

import time

import scenario
import scenario.test


class SuperScenario(scenario.Scenario):

    class ConfigKey(scenario.enum.StrEnum):
        SUBSCENARIO_PATH = "scenario.test.SuperScenario.subscenario_path"

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Sub-scenario sample")

        self.subscenario_path = scenario.Path(
            scenario.conf.get(SuperScenario.ConfigKey.SUBSCENARIO_PATH, type=str, default=scenario.test.paths.SIMPLE_SCENARIO),
        )  # type: scenario.Path

    def step001(self):  # type: (...) -> None  # location: step001
        self.STEP("Sub-scenario execution")

        _t0 = 0.0  # type: float
        _tf = 0.0  # type: float
        if self.ACTION("Execute the '%s' scenario." % self.subscenario_path):
            _t0 = time.time()
            scenario.runner.executepath(self.subscenario_path)
            _tf = time.time()

        if self.RESULT("No exception is thrown."):
            self.evidence("Sub-scenario executed successfully in %.3f seconds" % (_tf - _t0))
