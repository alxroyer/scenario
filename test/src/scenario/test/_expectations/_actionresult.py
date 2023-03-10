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

import typing

import scenario

if typing.TYPE_CHECKING:
    from ._scenario import ScenarioExpectations as ScenarioExpectationsType
    from ._step import StepExpectations as StepExpectationsType


class ActionResultExpectations:
    def __init__(
            self,
            step_expectations,  # type: StepExpectationsType
    ):  # type: (...) -> None
        self.step_expectations = step_expectations  # type: StepExpectationsType

        self.type = scenario.ActionResult.Type.ACTION  # type: scenario.ActionResult.Type
        self.description = None  # type: typing.Optional[str]
        self.subscenario_expectations = None  # type: typing.Optional[typing.List[ScenarioExpectationsType]]

    def addsubscenario(
            self,
            subscenario_expectations,  # type: ScenarioExpectationsType
    ):  # type: (...) -> ScenarioExpectationsType
        if self.subscenario_expectations is None:
            self.subscenario_expectations = []
        self.subscenario_expectations.append(subscenario_expectations)
        return subscenario_expectations

    def nosubscenarios(self):  # type: (...) -> None
        assert self.subscenario_expectations is None
        self.subscenario_expectations = []
