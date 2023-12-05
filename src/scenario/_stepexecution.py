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
Step execution management.
"""

import typing

if typing.TYPE_CHECKING:
    from ._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from ._executionstatus import ExecutionStatus as _ExecutionStatusType
    from ._stepdefinition import StepDefinition as _StepDefinitionType


class StepExecution:
    """
    Step execution information.

    .. note::
        Due to the :ref:`goto feature <goto>`, a step may be executed several times.
        By the way, a :class:`._stepdefinition.StepDefinition` instance may own multiple instances of :class:`StepExecution`.
    """

    def __init__(
            self,
            definition,  # type: _StepDefinitionType
            number,  # type: int
    ):  # type: (...) -> None
        """
        Initializes a new step execution for the given step definition.

        Starts the execution time with the current date.

        :param definition: Step definition this instance describes an execution for.
        :param number: Execution number. See :attr:`number`.
        """
        from ._stats import TimeStats
        from ._testerrors import TestError

        #: Owner step reference.
        self.definition = definition  # type: _StepDefinitionType
        #: Step execution number.
        #:
        #: Execution number of this step execution within the steps executions of the related scenario.
        #: Starting from 1, as displayed to the user.
        self.number = number  # type: int

        #: Current action or expected result under execution.
        #:
        #: Differs from :attr:`StepExecutionHelper.current_action_result_definition_index` in that this reference can be set to ``None``
        #: when the action / expected result execution is done.
        self.current_action_result_definition = None  # type: typing.Optional[_ActionResultDefinitionType]
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats
        #: Error.
        self.errors = []  # type: typing.List[TestError]
        #: Warnings.
        self.warnings = []  # type: typing.List[TestError]

        self.time.setstarttime()

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflection import qualname

        return f"<{qualname(type(self))}#{self.number} of {self.definition!r}>"

    @property
    def status(self):  # type: () -> _ExecutionStatusType
        """
        Step execution status.

        :return:
            Step execution status:

            - :attr:`._executionstatus.ExecutionStatus.FAIL` when at least one error is set.
            - :attr:`._executionstatus.ExecutionStatus.WARNINGS` when at least one warning is set.
            - :attr:`._executionstatus.ExecutionStatus.SUCCESS` if the execution has passed without errors or warnings.
            - :attr:`._executionstatus.ExecutionStatus.UNKNOWN` if the execution is not terminated.
        """
        from ._executionstatus import ExecutionStatus

        if self.errors:
            return ExecutionStatus.FAIL
        elif self.warnings:
            return ExecutionStatus.WARNINGS
        elif self.time.end is not None:
            return ExecutionStatus.SUCCESS
        else:
            return ExecutionStatus.UNKNOWN


class StepExecutionHelper:
    """
    Step execution helper methods.

    Avoids the public exposition of methods for internal implementation only.
    """

    def __init__(
            self,
            execution,  # type: StepExecution
    ):  # type: (...) -> None
        """
        Instanciates a helper for the given step execution.

        :param execution: Step execution instance this helper works for.
        """
        #: Step execution instance this helper works for.
        self.execution = execution

    @property
    def current_action_result_definition_index(self):  # type: () -> int
        """
        Current action or expected result index under execution.

        Retrieves the information stored with :attr:`execution`.
        """
        if not hasattr(self.execution, "__current_action_result_definition_index"):
            setattr(self.execution, "__current_action_result_definition_index", -1)
        return int(getattr(self.execution, "__current_action_result_definition_index"))

    @current_action_result_definition_index.setter
    def current_action_result_definition_index(self, value):  # type: (int) -> None
        """
        Current action or expected result index under execution.

        Stores the information with :attr:`execution`.
        """
        setattr(self.execution, "__current_action_result_definition_index", value)

    def getnextactionresultdefinition(self):  # type: (...) -> _ActionResultDefinitionType
        """
        Retrieves the next action/result definition to execute.

        :return: Next :class:`._actionresultdefinition.ActionResultDefinition` instance to execute.

        Sets the :attr:`StepExecution.current_action_result_definition` reference by the way.
        """
        # Increment the current action/result definition index.
        self.current_action_result_definition_index += 1

        # Set the `current_action_result_definition` reference.
        self.execution.current_action_result_definition = self.execution.definition.getactionresult(self.current_action_result_definition_index)

        return self.execution.current_action_result_definition
