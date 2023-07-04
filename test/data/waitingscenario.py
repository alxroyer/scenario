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

import time
import typing

import scenario


class WaitingScenario(scenario.Scenario):

    def __init__(self):  # type: (...) -> None
        scenario.Scenario.__init__(
            self,
            title="Waiting scenario",
        )

        scenario.handlers.install(
            scenario.Event.BEFORE_TEST,
            self._beforetest,
            scenario=self, once=True,
        )
        scenario.handlers.install(
            scenario.Event.AFTER_TEST,
            self._aftertest,
            scenario=self, once=True,
        )

    def _beforetest(
            self,
            event,  # type: str
            data,  # type: typing.Any
    ):  # type: (...) -> None
        self.info("Waiting for 1 second before the test")
        time.sleep(1.0)

    def step010(self):  # type: (...) -> None
        self.STEP("Waiting step")

        if self.ACTION("Wait for 5 seconds"):
            time.sleep(5.0)

    def _aftertest(
            self,
            event,  # type: str
            data,  # type: typing.Any
    ):  # type: (...) -> None
        self.info("Waiting for 2 seconds after the test")
        time.sleep(2.0)
