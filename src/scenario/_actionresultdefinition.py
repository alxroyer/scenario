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

"""
Action / expected result definition.
"""

import typing

if True:
    from . import _enumutils as _enumutils  # @inheritance
    from . import _textutils as _textutils  # @perf
if typing.TYPE_CHECKING:
    from ._actionresultexecution import ActionResultExecution as _ActionResultExecutionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType


class ActionResultDefinition:
    """
    This class describes both an action or an expected result.
    """

    class Type(_enumutils.StrEnum):
        """
        Enum that tells whether a user text defines an action or an expected result.
        """
        #: Action type.
        ACTION = "ACTION"
        #: Expected result type.
        RESULT = "RESULT"

    def __init__(
            self,
            type,  # type: ActionResultDefinition.Type  # noqa  ## Shadows built-in name 'type'
            description,  # type: _textutils.AnyLongTextType
    ):  # type: (...) -> None
        """
        :param type: Action/result type.
        :param description: User description for this action/result.

        .. note:: As it makes the API convenient, we deliberately shadow the built-in with the ``type`` parameter.
        """
        #: Action/result type.
        self.type = type  # type: ActionResultDefinition.Type
        #: Action/result textual description.
        self.description = _textutils.anylongtext2str(description)  # type: str
        #: Owner step.
        #:
        #: Set when :meth:`._stepdefinition.StepDefinition.addactionresult()` is called.
        self._step = None  # type: typing.Optional[_StepDefinitionType]
        #: Executions.
        self.executions = []  # type: typing.List[_ActionResultExecutionType]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        return f"<{self.type} {self.description!r}>"

    def __str__(self):  # type: () -> str
        """
        Printable string representation.
        """
        return f"{self.type} {self.description!r}"

    @property
    def step(self):  # type: () -> _StepDefinitionType
        """
        Owner step.
        """
        if self._step is None:
            raise RuntimeError(f"Owner step not set yet for {self!r}")
        return self._step

    @step.setter
    def step(self, step):  # type: (_StepDefinitionType) -> None
        """
        Owner step setter.

        Called once by :meth:`._stepdefinition.StepDefinition.addactionresult()`.
        """
        if self._step is not None:
            raise RuntimeError(f"Owner step already set for {self!r} with {self._step!r}, can't set {step!r}")
        self._step = step

    @property
    def number(self):  # type: () -> int
        """
        Action/result definition number.

        Number of this action/result definition within the actions/results defining the related step.
        Starting from 1, as displayed to the user.
        """
        _action_result_number = 0  # type: int
        for _action_result_definition in self.step.actions_results:  # type: ActionResultDefinition
            _action_result_number += 1
            if _action_result_definition is self:
                break
        return _action_result_number
