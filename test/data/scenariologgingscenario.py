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


class ScenarioLoggingScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Scenario logging scenario sample")

    def step000(self):  # type: (...) -> None
        self.STEP("Scenario logging")

        scenario.logging.debug("Logging before actions/results")

        if self.ACTION("This is a sample action."):
            scenario.logging.debug("Action logging")
            self.evidence("Action evidence.")
        if self.RESULT("This is a sample expected result."):
            scenario.logging.debug("Expected result logging")
            self.evidence("Expected result evidence.")

        scenario.logging.debug("Logging after actions/results")
