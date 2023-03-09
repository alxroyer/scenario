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

import time
import typing

if typing.TYPE_CHECKING:
    from ._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from ._stats import ExecTotalStats as _ExecTotalStatsType
    from ._stepdefinition import StepDefinition as _StepDefinitionType


class StepExecution:
    """
    Step execution information.

    .. note:: Due to the :ref:`*goto* feature <goto>`, a step may be executed several times.
              By the way, a :class:`.stepdefinition.StepDefinition` instance may own multiple instances of :class:`StepExecution`.
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
        #: Differs from :attr:`__current_action_result_definition_index` in that this reference can be set to ``None``
        #: when the action / expected result execution is done.
        self.current_action_result_definition = None  # type: typing.Optional[_ActionResultDefinitionType]
        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats
        #: Error.
        self.errors = []  # type: typing.List[TestError]
        #: Warnings.
        self.warnings = []  # type: typing.List[TestError]

        #: Current action or expected result index under execution.
        self.__current_action_result_definition_index = -1  # type: int

        self.time.setstarttime()

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflex import qualname

        return f"<{qualname(type(self))}#{self.number} of {self.definition!r}>"

    def getnextactionresultdefinition(self):  # type: (...) -> _ActionResultDefinitionType
        """
        Retrieves the next action/result definition to execute.

        :return: Next :class:`.actionresultdefinition.ActionResultDefinition` instance to execute.

        Sets the :attr:`current_action_result_definition` reference by the way.
        """
        # Increment the current action/result definition index.
        self.__current_action_result_definition_index += 1

        # Set the `current_action_result_definition` reference.
        self.current_action_result_definition = self.definition.getactionresult(self.__current_action_result_definition_index)

        return self.current_action_result_definition

    def getstarttime(self):  # type: (...) -> float
        """
        Retrieves the starting time of the step execution.

        :return: Step execution start time.
        """
        assert self.time.start is not None, f"{self.definition} not started"
        return self.time.start

    def getendtime(
            self,
            expect,  # type: bool
    ):  # type: (...) -> float
        """
        Retrieves the ending time of the step execution.

        :param expect: ``True`` when this step execution is expected to be terminated. Otherwise, the current time is returned.
        :return: Step execution end time, or current time.
        """
        if self.time.end is not None:
            return self.time.end
        elif expect:
            raise AssertionError(f"{self.definition} not terminated")
        else:
            return time.time()

    @staticmethod
    def actionstats(
            definition,  # type: _StepDefinitionType
    ):  # type: (...) -> _ExecTotalStatsType
        """
        Computes action statistics for the given step definition.

        :param definition: Step definition to compute action statistics for.
        :return: Action statistics of the step.
        """
        from ._actionresultdefinition import ActionResultDefinition
        from ._stats import ExecTotalStats

        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _action_result_definition in definition.actions_results:  # type: ActionResultDefinition
            if _action_result_definition.type == ActionResultDefinition.Type.ACTION:
                _stats.total += 1
                _stats.executed += len(_action_result_definition.executions)
        return _stats

    @staticmethod
    def resultstats(
            definition,  # type: _StepDefinitionType
    ):  # type: (...) -> _ExecTotalStatsType
        """
        Computes expected result statistics for the given step definition.

        :param definition: Step definition to compute expected result statistics for.
        :return: Expected result statistics of the step.
        """
        from ._actionresultdefinition import ActionResultDefinition
        from ._stats import ExecTotalStats

        _stats = ExecTotalStats()  # type: ExecTotalStats
        for _action_result_definition in definition.actions_results:  # type: _ActionResultDefinitionType
            if _action_result_definition.type == ActionResultDefinition.Type.RESULT:
                _stats.total += 1
                _stats.executed += len(_action_result_definition.executions)
        return _stats
