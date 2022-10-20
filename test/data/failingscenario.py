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

import typing

import scenario


class FailingScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(self)

        self.setattribute("TITLE", "Failing scenario sample")

        self.last_checkpoint = None  # type: typing.Optional[str]

    def step010(self):  # type: (...) -> None  # location: step010
        self.STEP("Step in failure")

        if self.ACTION("Memorize 'step010-1' as the last checkpoint."):
            self.last_checkpoint = "step010-1"
            self.evidence("Last checkpoint: '%s'" % self.last_checkpoint)

        if self.ACTION("Generate an exception without catching it."):
            self.fail("This is an exception.")  # location: step010-exception
        if self.RESULT("The exception is thrown."):
            pass

        if self.ACTION("Memorize 'step010-2' as the last checkpoint."):
            self.last_checkpoint = "step010-2"
            self.evidence("Last checkpoint: '%s'" % self.last_checkpoint)

    def step020(self):  # type: (...) -> None  # location: step020
        self.STEP("Successful step")

        if self.ACTION("Check the last checkpoint."):
            self.evidence("Last checkpoint: '%s'" % self.last_checkpoint)
        if self.RESULT("The last checkpoint is... whatever."):
            pass

        if self.ACTION("Memorize 'step020-1' as the last checkpoint."):
            self.last_checkpoint = "step020-1"
            self.evidence("Last checkpoint: '%s'" % self.last_checkpoint)
