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


class InvalidScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Invalid scenario sample")

    def step010(self):  # type: (...) -> None
        self.STEP("step#10")

        if self.ACTION("Embed a syntax error in this script."):
            syntax error  # location: syntax-error
