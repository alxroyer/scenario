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
Assertion helpers.

Functions, types and constants for the :class:`.assertions.Assertions` class.
"""

import typing
import unittest as _unittestmod

if typing.TYPE_CHECKING:
    # Same as `StepExecution` in 'assertions.py'.
    from .stepdefinition import StepDefinition, StepSpecificationType
    # Same as `StepExecution` in 'assertions.py'.
    from .stepexecution import StepExecution


if typing.TYPE_CHECKING:
    #: Optional error parameter type.
    ErrParamType = typing.Optional[str]

    #: Evidence parameter type.
    EvidenceParamType = typing.Optional[typing.Union[bool, str]]

    #: Comparable type.
    #:
    #: Declared as a :class:`typing.TypeVar` so that every :class:`Comparable` parameter within the same function call is of the same type.
    ComparableType = typing.TypeVar("ComparableType", int, float, str)

    #: Type representing a type, or a set of types.
    TypeOrTypesType = typing.Optional[typing.Union[type, typing.Iterable[type]]]

    #: Item type.
    #:
    #: Declared as a :class:`typing.TypeVar` so that item and iterable parameters within the same function call are set with consistent types.
    ItemType = typing.TypeVar("ItemType")

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
    StepExecutionSpecificationType = typing.Union[StepSpecificationType, StepExecution]


__doc__ += """
.. py:attribute:: unittest

    :class:`unittest.TestCase` instance used to call :mod:`unittest` assertion functions.
"""
unittest = _unittestmod.TestCase()  # type: _unittestmod.TestCase


def safecontainer(
        obj,  # type: typing.Iterable[ItemType]
):  # type: (...) -> typing.Union[str, bytes, typing.List[ItemType]]
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


def saferepr(
        obj,  # type: typing.Any
        max_length=256,  # type: int
        focus=None,  # type: typing.Any
):  # type: (...) -> str
    """
    Safe representation of an object.

    :param obj: Object to represent.
    :param max_length: Representation maximum length.
    :param focus: Data to focus on.
    :return: Object representation.

    .. note:: Inspired from :mod:`unittest`.
    """
    # ``focus`` parameter is set.
    if (focus is (str, bytes)) and isinstance(obj, type(focus)):
        _start = 0  # type: int
        _end = len(obj)  # type: int
        if len(obj) > max_length:
            _start = obj.find(focus)
            _start -= 10
            if _start < 0:
                _start = 0
            _end = _start + max_length
            if _end > len(obj):
                _start -= (_end - len(obj))
                _end = len(obj)
        _anystr = type(obj)()  # type: typing.Union[str, bytes]
        if _start > 0:
            if isinstance(_anystr, str):
                _anystr += "...[truncated] "
            if isinstance(_anystr, bytes):
                _anystr += b'...[truncated] '
        _anystr += obj[_start:_end]
        if _end < len(obj):
            if isinstance(_anystr, str):
                _anystr += " [truncated]..."
            if isinstance(_anystr, bytes):
                _anystr += b' [truncated]...'
        return repr(_anystr)

    # ``focus`` parameter not set.
    # noinspection PyBroadException
    try:
        _repr = repr(obj)
    except Exception:
        _repr = object.__repr__(obj)
    if len(_repr) <= max_length:
        return _repr
    return _repr[:max_length] + " [truncated]..." + _repr[-1:]


def errmsg(
        optional,  # type: ErrParamType
        standard,  # type: str
):  # type: (...) -> str
    """
    Formats an error message: the optional and/or the regular one.

    :param optional: Optional assertion message, if set.
    :param standard: Standard assertion message.
    :return: Error message.
    """
    # noinspection PyProtectedMember
    return unittest._formatMessage(optional, standard)


def ctxmsg(
        context,  # type: str
        err,  # type: str
):  # type: (...) -> str
    """
    Builds an contextual assertion message.

    :param context: Context pattern, basically the methods name (e.g.: :const:`'assertisinstance()'`).
    :param err: Detailed assertion message.
    :return: Assertion message.
    """
    return "%s: %s" % (context, err)


def isnonemsg(
        context,  # type: str
        what,  # type: str
):  # type: (...) -> str
    """
    Builds an assertion message indicating that an element in unexpectedly :const:`None`.

    :param context: Context pattern, basically the methods name (e.g.: :const:`'assertisinstance()'`).
    :param what: Name of the parameter, or element, unexpectedly :const:`None` (e.g.: ``"obj"`` for a ``obj`` parameter).
    :return: Assertion message.
    """
    return ctxmsg(context, "%s unexpectedly None" % what)


def evidence(
        evidence_enabled,  # type: EvidenceParamType
        regular,  # type: str
):  # type: (...) -> None
    """
    Tracks assertion data, depending on the current scenario configuration

    :param evidence_enabled: Proof message activation and/or specialization (see the :ref:`dedicated note <assertions.evidence-param>`).
    :param regular: Regular proof message.
    """
    from .scenariorunner import SCENARIO_RUNNER
    from .scenariostack import SCENARIO_STACK

    if evidence_enabled and SCENARIO_RUNNER.doexecute():
        if SCENARIO_STACK.current_scenario_definition and SCENARIO_STACK.current_action_result_execution:
            if isinstance(evidence_enabled, str):
                _evidence = "%s: %s" % (evidence_enabled, regular)  # type: str
            else:
                _evidence = regular
            SCENARIO_STACK.current_scenario_definition.evidence(_evidence)


def getstepexecution(
        step_execution_specification,  # type: StepExecutionSpecificationType
):  # type: (...) -> StepExecution
    """
    Retrieves the (last) :class:`.stepexecution.StepExecution` instance corresponding to the given specification.

    :param step_execution_specification: Step execution specification (see :attr:`.assertionhelpers.StepExecutionSpecType`).
    :return: Step execution corresponding to the given specification.
    :raise: Exception when the step execution could not be found.
    """
    from .scenariostack import SCENARIO_STACK
    from .stepexecution import StepExecution

    if isinstance(step_execution_specification, StepExecution):
        return step_execution_specification

    assert SCENARIO_STACK.current_scenario_definition, "No current scenario"
    _step_definition = SCENARIO_STACK.current_scenario_definition.expectstep(step_execution_specification)  # type: StepDefinition
    assert _step_definition.executions, "No execution for %s" % str(_step_definition)
    return _step_definition.executions[-1]
