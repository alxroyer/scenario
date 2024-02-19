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

Helper functions, types and constants for :class:`._assertions.Assertions`,
publicly exposed for assertion routine definitions in user code.
"""

import typing
import unittest as _unittestmod

if True:
    from ._debugutils import FmtAndArgs as _FmtAndArgsImpl  # `FmtAndArgs` imported once for performance concerns.
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._debugutils import DelayedStr as _DelayedStrType
    from ._debugutils import FmtAndArgs as _FmtAndArgsType


if typing.TYPE_CHECKING:
    #: Optional error parameter type.
    ErrParamType = typing.Optional[typing.Union[str, _DelayedStrType]]

    #: Evidence parameter type.
    EvidenceParamType = typing.Optional[typing.Union[bool, str]]


#: ``unittest.TestCase`` instance used to call ``unittest`` assertion functions.
unittest = _unittestmod.TestCase()  # type: _unittestmod.TestCase


def errmsg(
        optional,  # type: ErrParamType
        standard,  # type: typing.Union[str, _DelayedStrType]
        *args  # type: typing.Any
):  # type: (...) -> str
    """
    Formats an error message: the optional and/or the regular one.

    :param optional: Optional assertion message, if set.
    :param standard: Standard assertion message.
    :param args: Standard assertion message arguments.
    :return: Error message.
    """
    # Ensure `optional` is of type `str` (if not `None`).
    if (optional is not None) and (not isinstance(optional, str)):
        optional = str(optional)
    # Ensure `standard` is of type `str`.
    if not isinstance(standard, str):
        standard = str(standard)
    # Format `standard` with `args` if not empty.
    if args:
        standard = str(_FmtAndArgsImpl(standard, *args))

    return unittest._formatMessage(optional, standard)  # noqa  ## Access to a protected member


def ctxmsg(
        context,  # type: str
        err,  # type: typing.Union[str, _DelayedStrType]
        *args  # type: typing.Any
):  # type: (...) -> str
    """
    Builds an contextual assertion message.

    :param context: Context pattern, basically the methods name (e.g.: ``"assertisinstance()"``).
    :param err: Detailed assertion message.
    :param args: Detailed assertion message arguments
    :return: Assertion message.
    """
    # Ensure `err` is of type `str`.
    if not isinstance(err, str):
        err = str(err)
    # Format `err` with `args` if not empty.
    if args:
        err = str(_FmtAndArgsImpl(err, *args))

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
        regular,  # type: typing.Union[str, _DelayedStrType]
        *args,  # type: typing.Any
):  # type: (...) -> None
    """
    Tracks assertion data, depending on the current scenario configuration

    :param evidence_enabled: Proof message activation and/or specialization (see the :ref:`dedicated note <assertions.evidence-param>`).
    :param regular: Regular proof message.
    :param args: Proof message arguments.
    """
    from ._scenariorunner import SCENARIO_RUNNER

    if evidence_enabled and SCENARIO_RUNNER.doexecute():
        if _FAST_PATH.scenario_stack.current_scenario_definition and _FAST_PATH.scenario_stack.current_action_result_execution:
            # Ensure `regular` is of type `str`.
            if not isinstance(regular, str):
                regular = str(regular)

            # Build the evidence message.
            _evidence_message = _FmtAndArgsImpl()  # type: _FmtAndArgsType
            if isinstance(evidence_enabled, str):
                _evidence_message.push("%s: ", evidence_enabled)
            _evidence_message.push(regular, *args)

            # Save it.
            _FAST_PATH.scenario_stack.current_scenario_definition.evidence(str(_evidence_message))
