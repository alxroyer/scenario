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
Assertion helpers.

Functions, types and constants for the :class:`.assertions.Assertions` class.
"""

import typing
import unittest as _unittestmod

if typing.TYPE_CHECKING:
    from .debugutils import DelayedStr as DelayedStrType
    from .stepdefinition import StepSpecificationType
    from .stepexecution import StepExecution as StepExecutionType


if typing.TYPE_CHECKING:
    #: Optional error parameter type.
    ErrParamType = typing.Optional[typing.Union[str, DelayedStrType]]

    #: Evidence parameter type.
    EvidenceParamType = typing.Optional[typing.Union[bool, str]]

    #: Comparable type.
    #:
    #: Declared as a :class:`typing.TypeVar` so that every :class:`Comparable` parameter within the same function call is of the same type.
    VarComparableType = typing.TypeVar("VarComparableType", int, float, str)

    #: Type representing a type, or a set of types.
    TypeOrTypesType = typing.Optional[typing.Union[type, typing.Iterable[type]]]

    #: Item type.
    #:
    #: Declared as a :class:`typing.TypeVar` so that item and iterable parameters within the same function call are set with consistent types.
    VarItemType = typing.TypeVar("VarItemType")

    #: Step execution specification.
    #:
    #: Either:
    #: - a string representation (see :attr:`.stepdefinition.StepSpecificationType`),
    #: - a step definition class (see :attr:`.stepdefinition.StepSpecificationType` as well),
    #: - or the step execution instance directly.
    #:
    #: When the specification is a string or a step class, the step execution is determined the following way:
    #: 1. Use the current scenario.
    #: 2. Find the step definition corresponding to the specification.
    #: 3: Retrieve its last execution.
    #:
    #: If a string or step class only is not enough to find out the expected step execution,
    #: the step execution instance may be passed on directly.
    StepExecutionSpecificationType = typing.Union[StepSpecificationType, StepExecutionType]


__doc__ += """
.. py:attribute:: unittest

    :class:`unittest.TestCase` instance used to call ``unittest`` assertion functions.
"""
unittest = _unittestmod.TestCase()  # type: _unittestmod.TestCase


def safecontainer(
        obj,  # type: typing.Iterable[VarItemType]
):  # type: (...) -> typing.Union[str, bytes, typing.List[VarItemType]]
    """
    Ensures working with a string or list-like object.

    :param obj:
        Input iterable object.
    :return:
        String or list-like object:

        - may be used as is, in order to check its emptiness,
        - may be applied ``len()`` on it,
        - has a ``count()`` method,
        - ...
    """
    if isinstance(obj, (str, bytes, list)):
        return obj
    else:
        return list(obj)


def errmsg(
        optional,  # type: ErrParamType
        standard,  # type: typing.Union[str, DelayedStrType]
        *args  # type: typing.Any
):  # type: (...) -> str
    """
    Formats an error message: the optional and/or the regular one.

    :param optional: Optional assertion message, if set.
    :param standard: Standard assertion message.
    :param args: Standard assertion message arguments.
    :return: Error message.
    """
    from .debugutils import FmtAndArgs

    # Ensure `optional` is of type `str` (if not `None`).
    if (optional is not None) and (not isinstance(optional, str)):
        optional = str(optional)
    # Ensure `standard` is of type `str`.
    if not isinstance(standard, str):
        standard = str(standard)
    # Format `standard` with `args` if not empty.
    if args:
        standard = str(FmtAndArgs(standard, *args))

    # noinspection PyProtectedMember
    return unittest._formatMessage(optional, standard)


def ctxmsg(
        context,  # type: str
        err,  # type: typing.Union[str, DelayedStrType]
        *args  # type: typing.Any
):  # type: (...) -> str
    """
    Builds an contextual assertion message.

    :param context: Context pattern, basically the methods name (e.g.: ``"assertisinstance()"``).
    :param err: Detailed assertion message.
    :param args: Detailed assertion message arguments
    :return: Assertion message.
    """
    from .debugutils import FmtAndArgs

    # Ensure `err` is of type `str`.
    if not isinstance(err, str):
        err = str(err)
    # Format `err` with `args` if not empty.
    if args:
        err = str(FmtAndArgs(err, *args))

    return f"{context}: {err}"


def isnonemsg(
        context,  # type: str
        what,  # type: str
):  # type: (...) -> str
    """
    Builds an assertion message indicating that an element in unexpectedly ``None``.

    :param context: Context pattern, basically the methods name (e.g.: ``"assertisinstance()"``).
    :param what: Name of the parameter, or element, unexpectedly ``None`` (e.g.: ``"obj"`` for a ``obj`` parameter).
    :return: Assertion message.
    """
    return ctxmsg(context, "%s unexpectedly None", what)


def evidence(
        evidence_enabled,  # type: EvidenceParamType
        regular,  # type: typing.Union[str, DelayedStrType]
        *args,  # type: typing.Any
):  # type: (...) -> None
    """
    Tracks assertion data, depending on the current scenario configuration

    :param evidence_enabled: Proof message activation and/or specialization (see the :ref:`dedicated note <assertions.evidence-param>`).
    :param regular: Regular proof message.
    :param args: Proof message arguments.
    """
    from .debugutils import FmtAndArgs
    from .scenariorunner import SCENARIO_RUNNER
    from .scenariostack import SCENARIO_STACK

    if evidence_enabled and SCENARIO_RUNNER.doexecute():
        if SCENARIO_STACK.current_scenario_definition and SCENARIO_STACK.current_action_result_execution:
            # Ensure `regular` is of type `str`.
            if not isinstance(regular, str):
                regular = str(regular)

            # Build the evidence message.
            _evidence_message = FmtAndArgs()  # type: FmtAndArgs
            if isinstance(evidence_enabled, str):
                _evidence_message.push("%s: ", evidence_enabled)
            _evidence_message.push(regular, *args)

            # Save it.
            SCENARIO_STACK.current_scenario_definition.evidence(str(_evidence_message))


def getstepexecution(
        step_execution_specification,  # type: StepExecutionSpecificationType
):  # type: (...) -> StepExecutionType
    """
    Retrieves the (last) :class:`.stepexecution.StepExecution` instance corresponding to the given specification.

    :param step_execution_specification: Step execution specification (see :attr:`.assertionhelpers.StepExecutionSpecType`).
    :return: Step execution corresponding to the given specification.
    :raise: Exception when the step execution could not be found.
    """
    from .scenariostack import SCENARIO_STACK
    from .stepdefinition import StepDefinition
    from .stepexecution import StepExecution

    if isinstance(step_execution_specification, StepExecution):
        return step_execution_specification

    assert SCENARIO_STACK.current_scenario_definition, "No current scenario"
    _step_definition = SCENARIO_STACK.current_scenario_definition.expectstep(step_execution_specification)  # type: StepDefinition
    assert _step_definition.executions, f"No execution for {_step_definition}"
    return _step_definition.executions[-1]
