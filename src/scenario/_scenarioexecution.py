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
Scenario execution management.
"""

import abc
import typing

if True:
    from ._knownissues import KnownIssue as _KnownIssueImpl  # `KnownIssue` imported once for performance concerns.
    from ._reflection import qualname as _qualname  # `qualname()` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._executionstatus import ExecutionStatus as _ExecutionStatusType
    from ._logger import Logger as _LoggerType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stats import ExecTotalStats as _ExecTotalStatsType
    from ._stepdefinition import StepDefinition as _StepDefinitionType


class ScenarioExecution:
    """
    Object that gathers execution information for a scenario.

    The scenario execution information is not stored in the base :class:`._scenariodefinition.ScenarioDefinition` class for user scenario definitions.
    In order to avoid confusion, the dedicated members and methods are implemented in a separate class: :class:`ScenarioExecution`.
    """

    def __init__(
            self,
            definition,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> None
        """
        :param definition:
            Related scenario definition under execution.
            May be ``None`` when the :class:`ScenarioExecution` instance is created as a data container only.
        """
        from ._scenariorunner import SCENARIO_RUNNER
        from ._stats import TimeStats
        from ._testerrors import TestError

        #: Related scenario definition.
        self.definition = definition  # type: _ScenarioDefinitionType

        #: Current step reference in the scenario step list.
        self.__current_step_definition = None  # type: typing.Optional[_StepDefinitionType]
        #: Next step reference in the step list.
        #: Used when a :meth:`._stepuserapi.StepUserApi.goto()` call has been made.
        self.__next_step_definition = None  # type: typing.Optional[_StepDefinitionType]

        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats
        #: Errors.
        self.errors = []  # type: typing.List[TestError]
        #: Warnings.
        self.warnings = []  # type: typing.List[TestError]

        #: Make this class log as if it was part of the :class:`._scenariorunner.ScenarioRunner` execution.
        self._logger = SCENARIO_RUNNER  # type: _LoggerType

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        return f"<{_qualname(type(self))} {self.definition.name!r}>"

    # Execution methods.

    def startsteplist(self):  # type: (...) -> None
        """
        Initializes the step iterator.

        Once the step iterator has been initialized, the :attr:`current_step_definition` attribute gives the current step.
        If the scenario has no step of the kind, :attr:`current_step_definition` is ``None`` as a result.

        The :meth:`nextstep()` method then moves the iterator forward.
        """
        self.__current_step_definition = None
        self.__next_step_definition = None
        if self.definition.steps:
            self.__current_step_definition = self.definition.steps[0]

        if self.__current_step_definition is not None:
            self._logger.debug("Starting with %r", self.__current_step_definition)
        else:
            self._logger.debug("No step")

    def nextstep(self):  # type: (...) -> bool
        """
        Moves the step iterator forward.

        :return: ``True`` when a next step is ready, ``False`` otherwise.

        When :meth:`nextstep()` returns ``False``, the :attr:`current_step_definition` is ``None`` as a result.
        """
        # Check the current step at first.
        if self.__current_step_definition is None:
            self._logger.warning("Cannot move to next step while no current step")
            return False

        # Next step reference possibly set from the outside.
        # If so, jump directly to this step reference.
        if self.__next_step_definition is not None:
            self._logger.debug("Jumping to %r", self.__next_step_definition)
            self.__current_step_definition = self.__next_step_definition
            self.__next_step_definition = None
            return True

        # Find out the position of the current step.
        _step_definition_index = self.definition.steps.index(self.__current_step_definition)  # type: int
        _previous_step_definition = self.definition.steps[_step_definition_index]  # type: _StepDefinitionType

        # Switch to the next step.
        _step_definition_index += 1
        if _step_definition_index >= len(self.definition.steps):
            self._logger.debug("No more steps")
            self.__current_step_definition = None
            return False
        self.__current_step_definition = self.definition.steps[_step_definition_index]

        # Next step found.
        self._logger.debug("Moving from %r to %r`", _previous_step_definition, self.__current_step_definition)
        return True

    def setnextstep(
            self,
            step_definition,  # type: _StepDefinitionType
    ):  # type: (...) -> None
        """
        Arbitrary sets the next step for the step iterator.

        Useful for the :ref:`goto feature <goto>`.

        :param step_definition: Next step definition to execute.
        """
        self.__next_step_definition = step_definition

    @property
    def current_step_definition(self):  # type: () -> typing.Optional[_StepDefinitionType]
        """
        Current step definition being executed.
        """
        return self.__current_step_definition

    # Statistics & output.

    @property
    def status(self):  # type: () -> _ExecutionStatusType
        """
        Scenario execution status.

        :return:
            Scenario execution status:

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

    @property
    def step_stats(self):  # type: () -> _ExecTotalStatsType
        """
        Step statistics computation.

        :return: Number of steps executed over the number of steps defined.
        """
        from ._stats import ExecTotalStats
        from ._stepsection import StepSectionDescription

        _step_stats = ExecTotalStats()  # type: ExecTotalStats
        for _step_definition in self.definition.steps:  # type: _StepDefinitionType
            # Skip `StepSection` instances.
            if isinstance(_step_definition, StepSectionDescription):
                continue

            _step_stats.total += 1
            _step_stats.executed += len(_step_definition.executions)
        return _step_stats

    @property
    def action_stats(self):  # type: () -> _ExecTotalStatsType
        """
        Action statistics computation.

        :return: Number of actions executed over the number of actions defined.
        """
        from ._actionresultdefinition import ActionResultDefinition
        from ._stats import ExecTotalStats
        from ._stepsection import StepSectionDescription

        _action_stats = ExecTotalStats()  # type: ExecTotalStats
        for _step_definition in self.definition.steps:  # type: _StepDefinitionType
            # Skip `StepSection` instances.
            if isinstance(_step_definition, StepSectionDescription):
                continue

            for _action_result_definition in _step_definition.actions_results:  # type: ActionResultDefinition
                if _action_result_definition.type == ActionResultDefinition.Type.ACTION:
                    _action_stats.total += 1
                    _action_stats.executed += len(_action_result_definition.executions)

        return _action_stats

    @property
    def result_stats(self):  # type: () -> _ExecTotalStatsType
        """
        Expected result statistics computation.

        :return: Number of expected results executed over the number of expected results defined.
        """
        from ._actionresultdefinition import ActionResultDefinition
        from ._stats import ExecTotalStats
        from ._stepsection import StepSectionDescription

        _result_stats = ExecTotalStats()  # type: ExecTotalStats
        for _step_definition in self.definition.steps:  # type: _StepDefinitionType
            # Skip `StepSection` instances.
            if isinstance(_step_definition, StepSectionDescription):
                continue

            for _action_result_definition in _step_definition.actions_results:  # type: ActionResultDefinition
                if _action_result_definition.type == ActionResultDefinition.Type.RESULT:
                    _result_stats.total += 1
                    _result_stats.executed += len(_action_result_definition.executions)

        return _result_stats


class ScenarioExecutionHelper(abc.ABC):
    """
    Helper class for :class:`ScenarioExecution`.
    """

    @staticmethod
    def criticitysortkeyfunction(
            scenario_execution,  # type: ScenarioExecution
    ):  # type: (...) -> typing.Tuple[int, int, float, int, float]
        """
        Key function used to sort :class:`ScenarioExecution` items in terms of result criticity.

        :param scenario_execution:
            :class:`ScenarioExecution` instance to compute result criticty for.
        :return:
            5-terms tuple:

            1. Status score: the higher, the more critical,
            2. Number of unqualified level errors,
            3. Highest error level (or -INFINITY),
            4. Number of unqualified level warnings,
            5. Highest warning level (or -INFINITY).
        """
        from ._executionstatus import ExecutionStatus
        from ._testerrors import TestError

        def _statusscore():  # type: () -> int
            return {
                ExecutionStatus.SUCCESS: 0,
                ExecutionStatus.SKIPPED: 1,
                ExecutionStatus.WARNINGS: 2,
                ExecutionStatus.UNKNOWN: 3,
                ExecutionStatus.FAIL: 4,
            }[scenario_execution.status]

        def _unqualifiedlevels(test_errors):  # type: (typing.Sequence[TestError]) -> int
            return len(list(filter(
                lambda test_error: (not isinstance(test_error, _KnownIssueImpl)) or (test_error.level is None),
                test_errors,
            )))

        def _highestissuelevel(test_errors):  # type: (typing.Sequence[TestError]) -> float
            _issue_levels = [- float("inf")]  # type: typing.List[float]
            for _test_error in test_errors:  # type: TestError
                if isinstance(_test_error, _KnownIssueImpl) and (_test_error.level is not None):
                    _issue_levels.append(float(_test_error.level))
            return max(_issue_levels)

        return (
            _statusscore(),
            _unqualifiedlevels(scenario_execution.errors), _highestissuelevel(scenario_execution.errors),
            _unqualifiedlevels(scenario_execution.warnings), _highestissuelevel(scenario_execution.warnings),
        )
