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


class SimpleScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Simple scenario sample")

    def step010(self):  # type: (...) -> None  # location: step010
        self.STEP("step#10")

        if self.ACTION("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."):
            self.evidence("Lorem ipsum...")
        if self.RESULT("Et leo duis ut diam."):
            self.evidence("Et leo...")

    def step020(self):  # type: (...) -> None  # location: step020
        self.STEP("step#20")

        if self.ACTION("Vitae turpis massa sed elementum."):
            self.evidence("Vitae turpis...")
        if self.RESULT("Faucibus a pellentesque sit amet."):
            self.evidence("Faucibus a pellentesque...")

    def step030(self):  # type: (...) -> None  # location: step030
        self.STEP("step#30")

        if self.ACTION("Quam id leo in vitae turpis massa sed elementum."):
            self.evidence("Quam id leo...")
        if self.RESULT("In aliquam sem fringilla ut morbi tincidunt augue interdum velit."):
            self.evidence("In aliquam sem...")
