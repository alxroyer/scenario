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


class GotoScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Goto scenario sample")

        self.a = 0  # type: int
        self.b = 0  # type: int

    def step000(self):  # type: (...) -> None  # location: step000
        self.STEP("Initializations")

        if self.ACTION("Initialize counter A with 0."):
            self.a = 0
            self.evidence("A = %d" % self.a)
        if self.ACTION("Initialize counter B with 0."):
            self.b = 0
            self.evidence("B = %d" % self.b)

    def step010(self):  # type: (...) -> None  # location: step010
        self.STEP("A++")

        if self.ACTION("Increment counter A."):
            self.a += 1
            self.evidence("A = %d" % self.a)

    def step020(self):  # type: (...) -> None  # location: step020
        self.STEP("A?")

        if self.ACTION("While A is lower than 2, go back to step<010>, otherwise jump over step<030> and go to step<050>."):
            self.evidence("A = %d" % self.a)
            if self.a < 2:
                self.goto("step010")
            else:
                self.goto("step040")

        if self.ACTION("Increment counter A."):
            self.a += 1

    def step030(self):  # type: (...) -> None  # location: step030
        self.STEP("B++")

        if self.ACTION("Increment counter B."):
            self.b += 1
            self.evidence("B = %d" % self.b)

    def step040(self):  # type: (...) -> None  # location: step040
        self.STEP("Check A and B")

        if self.RESULT("Check counter A equals 2."):
            self.evidence("A = %d" % self.a)
            self.assertequal(self.a, 2)
        if self.RESULT("Check counter B equals 0."):
            self.evidence("B = %d" % self.b)
            self.assertequal(self.b, 0)
