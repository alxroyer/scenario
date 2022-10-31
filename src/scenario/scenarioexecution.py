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

"""
Scenario execution management.
"""

import typing

# `ExecutionStatus` used in method signatures.
from .executionstatus import ExecutionStatus
# `ScenarioDefinition` used in method signatures.
from .scenariodefinition import ScenarioDefinition
# `ExecTotalStats` used in method signatures.
from .stats import ExecTotalStats
# `StepDefinition` used in method signatures.
from .stepdefinition import StepDefinition


class ScenarioExecution:
    """
    Object that gathers execution information for a scenario.

    The scenario execution information is not stored in the base :class:`.scenariodefinition.ScenarioDefinition` class for user scenario definitions.
    In order to avoid confusion, the dedicated members and methods are implemented in a separate class: :class:`ScenarioExecution`.
    """

    def __init__(
            self,
            definition,  # type: ScenarioDefinition
    ):  # type: (...) -> None
        """
        :param definition:
            Related scenario definition under execution.
            May be ``None`` when the :class:`ScenarioExecution` instance is created as a data container only.
        """
        from .logger import Logger
        from .scenariorunner import SCENARIO_RUNNER
        from .stats import TimeStats
        from .testerrors import TestError

        #: Related scenario definition.
        self.definition = definition  # type: ScenarioDefinition

        #: Current step reference in the scenario step list.
        self.__current_step_definition = None  # type: typing.Optional[StepDefinition]
        #: Next step reference in the step list.
        #: Used when a :meth:`.scenariodefinition.ScenarioDefinition.goto()` call has been made.
        self.__next_step_definition = None  # type: typing.Optional[StepDefinition]

        #: Time statistics.
        self.time = TimeStats()  # type: TimeStats
        #: Errors.
        self.errors = []  # type: typing.List[TestError]
        #: Warnings.
        self.warnings = []  # type: typing.List[TestError]

        #: Make this class log as if it was part of the :class:`ScenarioRunner` execution.
        self._logger = SCENARIO_RUNNER  # type: Logger

    def __repr__(self):  # type: (...) -> str
        """
        Canonical string representation.
        """
        from .reflex import qualname

        return f"<{qualname(type(self))} {self.definition.name!r}>"

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
        _previous_step_definition = self.definition.steps[_step_definition_index]  # type: StepDefinition

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
            step_definition,  # type: StepDefinition
    ):  # type: (...) -> None
        """
        Arbitrary sets the next step for the step iterator.

        Useful for the :ref:`goto feature <goto>`.

        :param step_definition: Next step definition to execute.
        """
        self.__next_step_definition = step_definition

    @property
    def current_step_definition(self):  # type: (...) -> typing.Optional[StepDefinition]
        """
        Current step definition being executed.

        Depends on the current active step iterator (see :meth:`backtosteptype()`).
        """
        return self.__current_step_definition

    # Statistics & output.

    @property
    def status(self):  # type: (...) -> ExecutionStatus
        """
        Scenario execution status.

        :attr:`.executionstatus.ExecutionStatus.FAIL` when an exception is set,
        :attr:`.executionstatus.ExecutionStatus.SUCCESS` otherwise.

        :return: Scenario execution status.
        """
        if self.errors:
            return ExecutionStatus.FAIL
        elif self.warnings:
            return ExecutionStatus.WARNINGS
        else:
            return ExecutionStatus.SUCCESS

    @property
    def step_stats(self):  # type: (...) -> ExecTotalStats
        """
        Step statistics computation.

        :return: Number of steps executed over the number of steps defined.
        """
        from .stepsection import StepSection

        _step_stats = ExecTotalStats()  # type: ExecTotalStats
        for _step_definition in self.definition.steps:  # type: StepDefinition
            # Skip `StepSection` instances.
            if isinstance(_step_definition, StepSection):
                continue

            _step_stats.total += 1
            _step_stats.executed += len(_step_definition.executions)
        return _step_stats

    @property
    def action_stats(self):  # type: (...) -> ExecTotalStats
        """
        Action statistics computation.

        :return: Number of actions executed over the number of actions defined.
        """
        from .stepexecution import StepExecution
        from .stepsection import StepSection

        _action_stats = ExecTotalStats()  # type: ExecTotalStats
        for _step_definition in self.definition.steps:  # type: StepDefinition
            # Skip `StepSection` instances.
            if isinstance(_step_definition, StepSection):
                continue

            _action_stats.add(StepExecution.actionstats(_step_definition))
        return _action_stats

    @property
    def result_stats(self):  # type: (...) -> ExecTotalStats
        """
        Expected result statistics computation.

        :return: Number of expected results executed over the number of expected results defined.
        """
        from .stepexecution import StepExecution
        from .stepsection import StepSection

        _result_stats = ExecTotalStats()  # type: ExecTotalStats
        for _step_definition in self.definition.steps:  # type: StepDefinition
            # Skip `StepSection` instances.
            if isinstance(_step_definition, StepSection):
                continue

            _result_stats.add(StepExecution.resultstats(_step_definition))
        return _result_stats

    # Comparison.
    def __cmp(
            self,
            other,  # type: typing.Any
    ):  # type: (...) -> int
        """
        Scenario execution comparison in terms of result criticity.

        :param other: Other :class:`ScenarioExecution` instance to compare with.
        :return:
            - -1 if ``self`` is less critical than ``other``,
            - 0 if ``self`` and ``other`` have the same criticity,
            - 1 if ``self`` is more critical than ``other``.
        """
        from .knownissues import KnownIssue
        from .testerrors import TestError

        if not isinstance(other, ScenarioExecution):
            raise TypeError(f"Cannot compare {self!r} with {other!r}")

        # Inner functions.
        def _statusscore(scenario_execution):  # type: (ScenarioExecution) -> int
            return {
                ExecutionStatus.SUCCESS: 0,
                ExecutionStatus.SKIPPED: 1,
                ExecutionStatus.WARNINGS: 2,
                ExecutionStatus.UNKOWN: 3,
                ExecutionStatus.FAIL: 4,
            }[scenario_execution.status]

        def _noissuelevels(test_errors):  # type: (typing.Sequence[TestError]) -> int
            _count = 0  # type: int
            for _test_error in test_errors:  # type: TestError
                if (not isinstance(_test_error, KnownIssue)) or (_test_error.level is None):
                    _count += 1
            return _count

        def _highesterrorissuelevel(test_errors):  # type: (typing.Sequence[TestError]) -> typing.Optional[int]
            _highest_error_issue_level = None  # type: typing.Optional[int]
            for _test_error in test_errors:  # type: TestError
                if isinstance(_test_error, KnownIssue) and (_test_error.level is not None):
                    if (_highest_error_issue_level is None) or (_test_error.level > _highest_error_issue_level):
                        _highest_error_issue_level = _test_error.level
            return _highest_error_issue_level

        # Compare status.
        if _statusscore(self) != _statusscore(other):
            return _statusscore(self) - _statusscore(other)

        # Compare errors:
        # - Without issue levels.
        if _noissuelevels(self.errors) != _noissuelevels(other.errors):
            return _noissuelevels(self.errors) - _noissuelevels(other.errors)
        # - Highest issue levels.
        _highest_error_issue_level1 = _highesterrorissuelevel(self.errors)  # type: typing.Optional[int]
        _highest_error_issue_level2 = _highesterrorissuelevel(other.errors)  # type: typing.Optional[int]
        if _highest_error_issue_level1 != _highest_error_issue_level2:
            if _highest_error_issue_level1 is None:
                return +1
            if _highest_error_issue_level2 is None:
                return -1
            return _highest_error_issue_level1 - _highest_error_issue_level2

        # Compare warnings:
        # - Without issue levels.
        if _noissuelevels(self.warnings) != _noissuelevels(other.warnings):
            return _noissuelevels(self.warnings) - _noissuelevels(other.warnings)
        # - Highest issue levels.
        _highest_warning_issue_level1 = _highesterrorissuelevel(self.warnings)  # type: typing.Optional[int]
        _highest_warning_issue_level2 = _highesterrorissuelevel(other.warnings)  # type: typing.Optional[int]
        if _highest_warning_issue_level1 != _highest_warning_issue_level2:
            if _highest_warning_issue_level1 is None:
                return +1
            if _highest_warning_issue_level2 is None:
                return -1
            return _highest_warning_issue_level1 - _highest_warning_issue_level2

        # Same criticity.
        return 0

    def __lt__(self, other):  # type: (typing.Any) -> bool
        """
        Checks whether ``self`` < ``other``, i.e. ``self`` strictly less critical than ``other``.
        """
        return self.__cmp(other) < 0

    def __le__(self, other):  # type: (typing.Any) -> bool
        """
        Checks whether ``self`` <= ``other``, i.e. ``self`` less critical than or as critical as``other``.
        """
        return self.__cmp(other) <= 0

    def __gt__(self, other):  # type: (typing.Any) -> bool
        """
        Checks whether ``self`` > ``other``, i.e. ``self`` strictly more critical than ``other``.
        """
        return self.__cmp(other) > 0

    def __ge__(self, other):  # type: (typing.Any) -> bool
        """
        Checks whether ``self`` >= ``other``, i.e. ``self`` more critical than or as critical as``other``.
        """
        return self.__cmp(other) >= 0

    # Do not use `__cmp()` for `__eq__()` nor `__ne__()`.
    # def __eq__(self, other): ...  # type: (typing.Any) -> bool
    # def __ne__(self, other): ...  # type: (typing.Any) -> bool
