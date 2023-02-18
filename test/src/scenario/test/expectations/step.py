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

# `ActionResultExpectations` used in method signatures.
from .actionresult import ActionResultExpectations
if typing.TYPE_CHECKING:
    from .scenario import ScenarioExpectations as ScenarioExpectationsType


class StepExpectations:
    def __init__(
            self,
            scenario_expectations,  # type: ScenarioExpectationsType
    ):  # type: (...) -> None
        self.scenario_expectations = scenario_expectations  # type: ScenarioExpectationsType

        self.number = None  # type: typing.Optional[int]
        self.name = None  # type: typing.Optional[str]
        self.description = None  # type: typing.Optional[str]
        self.action_result_expectations = None  # type: typing.Optional[typing.List[ActionResultExpectations]]

    def __str__(self):  # type: () -> str
        if self.number is not None:
            return f"step#{self.number}"
        if self.name is not None:
            return f"step<name={self.name!r}>"
        if self.description is not None:
            return f"step<description={self.description!r}>"
        return "step<?>"

    def addaction(
            self,
            action,  # type: str
    ):  # type: (...) -> ActionResultExpectations
        _action = ActionResultExpectations(self)  # type: ActionResultExpectations
        _action.type = scenario.ActionResult.Type.ACTION
        _action.description = action
        if self.action_result_expectations is None:
            self.action_result_expectations = []
        self.action_result_expectations.append(_action)
        return _action

    def addresult(
            self,
            result,  # type: str
    ):  # type: (...) -> ActionResultExpectations
        _result = ActionResultExpectations(self)  # type: ActionResultExpectations
        _result.type = scenario.ActionResult.Type.RESULT
        _result.description = result
        if self.action_result_expectations is None:
            self.action_result_expectations = []
        self.action_result_expectations.append(_result)
        return _result

    def action(
            self,
            action_result_index,  # type: int
    ):  # type: (...) -> ActionResultExpectations
        """
        Retrieves the corresponding :class:`ActionResultExpectations` object.

        :param action_result_index: Action/result index, starting from 0.
        :return: :class:`ActionResultExpectations` object.
        """
        assert self.action_result_expectations, "No action/result expectations yet"
        if self.action_result_expectations[action_result_index].type != scenario.ActionResult.Type.ACTION:
            raise KeyError(f"Action/result#{action_result_index}: Not an action")
        return self.action_result_expectations[action_result_index]

    def result(
            self,
            action_result_index,  # type: int
    ):  # type: (...) -> ActionResultExpectations
        """
        Retrieves the corresponding :class:`ActionResultExpectations` object.

        :param action_result_index: Action/result index, starting from 0.
        :return: :class:`ActionResultExpectations` object.
        """
        assert self.action_result_expectations, "No action/result expectations yet"
        if self.action_result_expectations[action_result_index].type != scenario.ActionResult.Type.RESULT:
            raise KeyError(f"Action/result#{action_result_index}: Not an expected result")
        return self.action_result_expectations[action_result_index]
