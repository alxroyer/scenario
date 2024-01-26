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
Step specifications.

Eases the way to define and retrieve a step definition or execution.
"""

import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._stepexecution import StepExecution as _StepExecutionType


class StepDefinitionSpecification:
    """
    Step definition specification resolution.

    Implementation for :obj:`AnyStepDefinitionSpecificationType`.
    """

    def __init__(
            self,
            step_specification,  # type: AnyStepDefinitionSpecificationType
    ):  # type: (...) -> None
        """
        Initializes a :class:`StepDefinitionSpecification` instance from any kind of type allowed by :obj:`AnyStepDefinitionSpecificationType`.

        :param step_specification: Input specification.
        """
        #: Single match specification (s-spec).
        self._s_spec = None  # type: typing.Optional[typing.Union[_StepDefinitionType, int]]
        #: Multiple match specification (m-spec).
        self._m_spec = None  # type: typing.Optional[typing.Union[typing.Type[_StepDefinitionType], str]]
        #: Multiple match index (mi-spec).
        self._m_spec_index = None  # type: typing.Optional[int]

        # Analyse `step_specification`.
        if isinstance(step_specification, StepDefinitionSpecification):
            self._s_spec = step_specification._s_spec
            self._m_spec = step_specification._m_spec
            self._m_spec_index = step_specification._m_spec_index
        elif isinstance(step_specification, (_FAST_PATH.step_definition_cls, int)):
            # Single match specifications (s-spec).
            self._s_spec = step_specification
        elif isinstance(step_specification, (str, type)):
            # Multiple match specifications (m-spec).
            self._m_spec = step_specification
        elif isinstance(step_specification, tuple):
            # Multiple match index (mi-spec).
            self._m_spec = step_specification[0]
            self._m_spec_index = step_specification[1]

        # Check *mi-spec* index value.
        if (self._m_spec_index is not None) and (self._m_spec_index < 0):
            raise ValueError(f"Multiple match index should not be negative ({self._m_spec_index!r} given)")

    def __str__(self):  # type: () -> str
        """
        Returns a human readable representation of the step specification.

        :return: String representation.
        """
        from ._reflection import qualname

        # Single match specifications (s-spec).
        if bool(isinstance(self._s_spec, _FAST_PATH.scenario_definition_cls)):  # Cast with `bool()` to avoid a "Statement is unreachable" error.
            return str(self._s_spec)
        if isinstance(self._s_spec, int):
            return f"step#{self._s_spec}"

        # Multiple match specifications (m-spec).
        _spec = ""  # type: str
        if isinstance(self._m_spec, str):
            _spec = repr(self._m_spec)
        if isinstance(self._m_spec, type):
            _spec = qualname(self._m_spec)

        # Multiple match index (mi-spec).
        if self._m_spec_index is not None:
            _spec = f"{_spec}[{self._m_spec_index}]"

        return _spec

    def resolve(
            self,
            scenario=None,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> typing.Optional[_StepDefinitionType]
        """
        Tries to resolve the step definition instance from the specification.

        :param scenario: Scenario to resolve the step from. Current scenario if not specified.
        :return: Step definition instance when resolved, ``None`` otherwise.
        """
        try:
            return self.expect(scenario=scenario)
        except LookupError:
            # Default to `None`.
            return None

    def expect(
            self,
            scenario=None,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> _StepDefinitionType
        """
        Resolves the step definition instance from the specification, or raises an exception.

        :param scenario: Scenario to resolve the step from. Current scenario if not specified.
        :return: Step definition instance resolved.
        :raise LookupError: When the step definition could not be found.
        """
        from ._scenariorunner import SCENARIO_RUNNER
        from ._scenariostack import SCENARIO_STACK

        # Ensure a scenario definition reference.
        if not scenario:
            scenario = SCENARIO_STACK.building.scenario_definition or SCENARIO_STACK.current_scenario_definition
        if not scenario:
            SCENARIO_STACK.raisecontexterror("No current scenario")

        # Identify matching steps.
        _matching_step_definitions = []  # type: typing.List[_StepDefinitionType]
        for _step_definition in scenario.steps:  # type: _StepDefinitionType
            if any([
                isinstance(self._s_spec, _FAST_PATH.step_definition_cls) and (_step_definition is self._s_spec),
                isinstance(self._s_spec, int) and (_step_definition.number == self._s_spec),
                isinstance(self._m_spec, str) and _step_definition.name.endswith(self._m_spec),
                isinstance(self._m_spec, type) and isinstance(_step_definition, self._m_spec),
            ]):
                _matching_step_definitions.append(_step_definition)
        if not _matching_step_definitions:
            raise LookupError(f"No step definition matching from scenario {scenario} with specification {self}")

        # Determine `_index`.
        _index = -1  # type: int
        if self._m_spec_index is not None:
            _index = self._m_spec_index
        # Avoid `_index` being unspecified when several steps match in *execution mode*.
        if (_index < 0) and (len(_matching_step_definitions) > 1) and SCENARIO_RUNNER.doexecute():
            raise LookupError(f"Ambiguous specification {self} from scenario {scenario}, index required in execution mode "
                              f"(matching steps {_matching_step_definitions!r})")

        # Return the step from the matching step list.
        try:
            return _matching_step_definitions[_index]
        except IndexError:
            raise LookupError(f"Could find step definition from scenario {scenario} with specification {self} "
                              f"(matching steps {_matching_step_definitions!r})")


class StepExecutionSpecification:
    """
    Step execution specification resolution.

    Implementation for :obj:`AnyStepExecutionSpecificationType`.
    """

    def __init__(
            self,
            step_specification,  # type: AnyStepExecutionSpecificationType
    ):  # type: (...) -> None
        """
        Initializes a :class:`StepExecutionSpecification` instance from any kind of type allowed by :obj:`AnyStepExecutionSpecificationType`.

        :param step_specification: Input specification.
        """
        from ._stepexecution import StepExecution

        #: Direct :class:`._stepexecution.StepExecution` instance.
        self._step_execution = None  # type: typing.Optional[_StepExecutionType]
        #: Step definition
        self._step_definition_spec = None  # type: typing.Optional[StepDefinitionSpecification]

        if isinstance(step_specification, StepExecutionSpecification):
            self._step_execution = step_specification._step_execution
            self._step_definition_spec = step_specification._step_definition_spec
        else:
            if isinstance(step_specification, StepExecution):
                self._step_execution = step_specification
            else:
                self._step_definition_spec = StepDefinitionSpecification(step_specification)

    def __str__(self):  # type: () -> str
        """
        Returns a human readable representation of the step specification.

        :return: String representation.
        """
        if self._step_execution is not None:
            return str(self._step_execution)
        if self._step_definition_spec is not None:
            return str(self._step_definition_spec)
        raise ValueError("Invalid step execution specification")

    def resolve(
            self,
            scenario=None,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> typing.Optional[_StepExecutionType]
        """
        Tries to resolves the step execution instance from the specification.

        :param scenario: Scenario to resolve the step from. Current scenario if not specified.
        :return: Step execution instance when resolved, ``None`` otherwise.
        """
        try:
            return self.expect(scenario=scenario)
        except LookupError:
            # Default to `None`.
            return None

    def expect(
            self,
            scenario=None,  # type: _ScenarioDefinitionType
    ):  # type: (...) -> _StepExecutionType
        """
        Resolves the step execution instance from the specification, or raises an exception.

        :param scenario: Scenario to resolve the step from. Current scenario if not specified.
        :return: Step execution instance resolved.
        :raise LookupError: When the step definition could not be found.
        """
        if self._step_execution is not None:
            return self._step_execution

        if self._step_definition_spec is not None:
            _step_definition = self._step_definition_spec.expect(scenario=scenario)  # type: _StepDefinitionType
            if not _step_definition.executions:
                raise LookupError(f"Step {_step_definition} not executed yet")
            return _step_definition.executions[-1]

        raise ValueError("Invalid step execution specification")


if typing.TYPE_CHECKING:
    #: Any step definition specification type.
    #:
    #: Either:
    #:
    #: 1. a :class:`StepDefinitionSpecification` instance (base implementation class for step definition specifications),
    #: 2. single match specifications (`s-spec`):
    #:
    #:    - a :class:`._stepdefinition.StepDefinition` instance directly,
    #:    - or an integer specifying the step definition number in its owner scenario,
    #:
    #: 3. multiple match specifications (`m-spec`):
    #:
    #:    - a step definition class,
    #:    - or a string representation, matching with the qualified name of the class or method (right part),
    #:
    #: 4. multiple match specifications with index (`mi-spec`):
    #:
    #:    - a tuple of a `m-spec`, refined with a non-negative number giving the index to consider in the list of matching steps.
    AnyStepDefinitionSpecificationType = typing.Union[
        StepDefinitionSpecification,
        # Single match specifications (s-spec).
        _StepDefinitionType,
        int,
        # Multiple match specifications (m-spec).
        typing.Type[_StepDefinitionType],
        str,
        # Multiple match with index (mi-spec).
        typing.Tuple[typing.Union[
            typing.Type[_StepDefinitionType],
            str,
        ], int],
    ]

    #: Any step execution specification type.
    #:
    #: Either:
    #:
    #: - a :class:`StepExecutionSpecification` instance (base implementation class for step execution specifications),
    #: - a :class:`._stepexecution.StepExecution` instance directly,
    #: - a step definition specification (:obj:`AnyStepDefinitionSpecificationType`).
    #:
    #: When the specification refers to a step definition, its last step execution is taken into account.
    AnyStepExecutionSpecificationType = typing.Union[
        StepExecutionSpecification,
        _StepExecutionType,
        AnyStepDefinitionSpecificationType,
    ]
