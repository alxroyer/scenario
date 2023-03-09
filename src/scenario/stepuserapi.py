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
User API methods for user :class:`.scenariodefinition.ScenarioDefinition` or :class:`.stepdefinition.StepDefinition` overloads.
"""

import abc
import typing

if typing.TYPE_CHECKING:
    from .issuelevels import AnyIssueLevelType
    from .stepdefinition import StepSpecificationType


class StepUserApi(abc.ABC):
    """
    Base class that defines the methods made available
    for user :class:`.scenariodefinition.ScenarioDefinition` or :class:`.stepdefinition.StepDefinition` overloads.
    """

    def __init__(self):  # type: (...) -> None
        """
        Initializes an empty known issue list.
        """
        from .knownissues import KnownIssue

        #: Known issues at the definition level.
        self.known_issues = []  # type: typing.List[KnownIssue]

    # noinspection PyPep8Naming
    def STEP(
            self,
            description,  # type: str
    ):  # type: (...) -> None
        """
        Defines the short description of a step.

        :param description: Step description.

        .. note:: We deliberately deviate from PEP8 namings in order to highlight :meth:`STEP` calls in the final test code.
        """
        from .scenariorunner import SCENARIO_RUNNER

        SCENARIO_RUNNER.onstepdescription(description)

    # noinspection PyPep8Naming
    def ACTION(
            self,
            action,  # type: str
    ):  # type: (...) -> bool
        """
        Describes a test action.

        :param action: Action description.
        :return: ``True`` when the test script shall be executed, ``False`` otherwise (documentation generation).

        .. note:: We deliberately deviate from PEP8 namings in order to highlight :meth:`ACTION` calls in the final test code.
        """
        from .actionresultdefinition import ActionResultDefinition
        from .scenariorunner import SCENARIO_RUNNER

        SCENARIO_RUNNER.onactionresult(ActionResultDefinition.Type.ACTION, action)

        return self.doexecute()

    # noinspection PyPep8Naming
    def RESULT(
            self,
            result,  # type: str
    ):  # type: (...) -> bool
        """
        Describes an expected result.

        :param result: Expected result description.
        :return: ``True`` when the test script shall be executed, ``False`` otherwise (documentation generation).

        .. note:: We deliberately deviate from PEP8 namings in order to highlight :meth:`RESULT` calls in the final test code.
        """
        from .actionresultdefinition import ActionResultDefinition
        from .scenariorunner import SCENARIO_RUNNER

        SCENARIO_RUNNER.onactionresult(ActionResultDefinition.Type.RESULT, result)

        return self.doexecute()

    def doexecute(self):  # type: (...) -> bool
        """
        Tells whether test script should be executed.

        :return:
            ``True`` for test execution, ``False`` for documentation generation only,
            exactly the same as the :meth:`ACTION()` and :meth:`RESULT()` methods do,
            but without generating any texts.
        """
        from .scenariorunner import SCENARIO_RUNNER

        return SCENARIO_RUNNER.doexecute()

    def evidence(
            self,
            evidence,  # type: str
    ):  # type: (...) -> None
        """
        Saves an evidence for the current action or expected result.

        :param evidence: Evidence text.
        """
        from .scenariorunner import SCENARIO_RUNNER

        if not isinstance(evidence, str):
            # In case the user provides something that is not a regular string.
            evidence = repr(evidence)  # type: ignore[unreachable]
        SCENARIO_RUNNER.onevidence(evidence)

    def goto(
            self,
            to_step_specification,  # type: StepSpecificationType
    ):  # type: (...) -> None
        """
        Makes the execution jump to the given step.

        :param to_step_specification: Step specification of the step to jump to (see :attr:`.stepdefinition.StepSpecificationType`).
        """
        from .scenariorunner import SCENARIO_RUNNER

        SCENARIO_RUNNER.goto(to_step_specification)

    @typing.overload
    def knownissue(
            self,
            __id,  # type: str
            __message,  # type: str
    ):  # type: (...) -> None
        """
        Deprecated.

        :param __id: Issue identifier.
        :param __message: Error message to display / store with.

        .. note::
            The double leading underscores indicates positional-only arguments
            (see https://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html#functions,
            inspired from https://stackoverflow.com/questions/56350385/overload-typings-with-python-args-in-super-class#56352650).
        """

    @typing.overload
    def knownissue(
            self,
            message,  # type: str
            level=None,  # type: AnyIssueLevelType
            id=None,  # type: str  # noqa  ## Shadows built-in name 'id'
    ):  # type: (...) -> None
        """
        Registers a known issue.

        :param message: Error message to display / store with.
        :param level: Issue level.
        :param id: Issue identifier.
        """

    def knownissue(
            self,
            *args,  # type: str
            **kwargs,  # type: typing.Any
    ):  # type: (...) -> None
        """
        General implementation for related overloads.
        """
        from .knownissues import KnownIssue
        from .logger import Logger
        from .scenariorunner import SCENARIO_RUNNER

        # Positional parameters (deprecated).
        if (len(args) == 2) and (not kwargs):
            if isinstance(self, Logger):
                self.warning(f"knownissue(): Positional parameters deprecated, please use named parameters")
            SCENARIO_RUNNER.onerror(KnownIssue(id=args[0], message=args[1]), originator=self)
            return

        # Ensure ``message`` as a named argument.
        if (len(args) == 1) and ("message" not in kwargs):
            kwargs["message"] = args[0]
        else:
            assert not args, "knownissue(): One positional argument at most for 'message'"

        # Build the `KnownIssue` objects with named arguments.
        for _arg_name in kwargs:
            assert _arg_name in ("level", "id", "message"), f"knownissue(): Wrong argument {_arg_name!r}"
        SCENARIO_RUNNER.onerror(KnownIssue(**kwargs), originator=self)
