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
Scenario execution stack.
"""

import typing

# `ActionResultDefinition` used in method signatures.
from .actionresultdefinition import ActionResultDefinition
# `ActionResultExecution` used in method signatures.
from .actionresultexecution import ActionResultExecution
if typing.TYPE_CHECKING:
    # `AnyIssueLevelType` used in method signatures.
    # Type declared for type checking only.
    from .issuelevels import AnyIssueLevelType
# `Logger` used for inheritance.
from .logger import Logger
# `ScenarioDefinition` used in method signatures.
from .scenariodefinition import ScenarioDefinition
# `ScenarioExecution` used in method signatures.
from .scenarioexecution import ScenarioExecution
# `StepDefinition` used in method signatures.
from .stepdefinition import StepDefinition
# `StepExecution` used in method signatures.
from .stepexecution import StepExecution
# `StepUserApi` used in method signatures.
from .stepuserapi import StepUserApi


class BuildingContext:
    """
    Storage of instances under construction.
    """

    def __init__(self):  # type: (...) -> None
        """
        Declares references of objects under construction.

        Objects under construction:

        - scenario definition,
        - but no step definition!

          .. warning::
              We do not store a step definition reference here, fed from :meth:`.stepdefinition.StepDefinition.__init__()` especially,
              for the reason that we cannot guarantee that the reference of a volatile step definition
              would not take the place of a real step definition being built.

              See :attr:`step_definition` and :meth:`fromoriginator()` for further details on the step definition reference management.
        """
        #: Scenario definitions being built.
        self.__scenario_definitions = []  # type: typing.List[ScenarioDefinition]

    def pushscenariodefinition(
            self,
            scenario_definition,  # type: ScenarioDefinition
    ):  # type: (...) -> None
        """
        Pushes the reference of the scenario definition being built to the building context of the scenario stack.

        :param scenario_definition: Scenario definition being built.
        """
        self.__scenario_definitions.append(scenario_definition)
        SCENARIO_STACK.debug("building.pushscenariodefinition(): scenario_definition = 0x%x / %r", id(scenario_definition), scenario_definition)
        SCENARIO_STACK.pushindentation()

    def popscenariodefinition(
            self,
            scenario_definition,  # type: ScenarioDefinition
    ):  # type: (...) -> None
        """
        Pops the reference of the scenario definition being built from the building context of the scenario stack.

        :param scenario_definition: Scenario definition being built.
        """
        if self.__scenario_definitions and (scenario_definition is self.__scenario_definitions[-1]):
            SCENARIO_STACK.popindentation()
            SCENARIO_STACK.debug("building.popscenariodefinition(): scenario_definition = 0x%x / %r", id(scenario_definition), scenario_definition)
            self.__scenario_definitions.pop()
        else:
            SCENARIO_STACK.raisecontexterror(
                f"building.popscenariodefinition(): No such scenario_definition "
                f"0x{id(scenario_definition):x} / {scenario_definition!r}",
            )

    @property
    def scenario_definition(self):  # type: (...) -> typing.Optional[ScenarioDefinition]
        """
        Main scenario definition being built (i.e. the first), if any.
        """
        if self.__scenario_definitions:
            return self.__scenario_definitions[0]
        else:
            return None

    @property
    def step_definition(self):  # type: (...) -> typing.Optional[StepDefinition]
        """
        Step definition being built, if any.

        The step definition being built is the one currently executed
        in :const:`.scenariorunner.ScenarioRunner.ExecutionMode.BUILD_OBJECTS` execution mode
        by :meth:`.scenariorunner.ScenarioRunner._buildscenario()`.

        .. warning::
            This does not cover the case of method calls directly made in a step object initializer,
            and especially for:

            - :meth:`.stepuserapi.StepUserApi.knownissue()`

            In order to cover such cases, theses methods shall set an ``originator`` parameter when calling :class:`.scenariorunner.ScenarioRunner` methods,
            to let the latter identify the appropriate instance being built with the help of the :meth:`fromoriginator()` method.
        """
        if self.scenario_definition and self.scenario_definition.execution:
            return self.scenario_definition.execution.current_step_definition
        return None

    def fromoriginator(
            self,
            originator,  # type: StepUserApi
    ):  # type: (...) -> StepUserApi
        """
        Determines the actual object being built.

        :param originator: :class:`.stepuserapi.StepUserApi` instance that made a call.
        :return: :class:`.stepuserapi.StepUserApi` actually being built.

        Fixes the ``originator`` reference from the current scenario definition being built
        to the current step definition being built if any.

        Lets the ``originator`` reference as is otherwise:

        - either a :class:`.stepdefinition.StepDefinition` reference directly,
        - or :class:`.scenariodefinition.ScenarioDefinition` reference.
        """
        if (originator is self.scenario_definition) and self.step_definition:
            # The call comes from the `ScenarioDefinition` being built, but a step definition is currently being built.
            # Return the latter in that case.
            return self.step_definition

        # Check scenario definition originators correspond to the scenario definition currently being built.
        # Should never happen, but if not, just display a warning.
        if isinstance(originator, ScenarioDefinition) and (originator is not self.scenario_definition):
            SCENARIO_STACK.warning(f"BuildingContext.fromoriginator(): Unexpected originator {originator!r}, {self.scenario_definition!r} expected")

        # Return the originator given by default.
        return originator


class ScenarioStack(Logger):
    """
    Scenario execution stack management.

    This class acts as a helper for the :class:`.scenariorunner.ScenarioRunner` class.

    It also determines the :ref:`scenario stack logging indentation <logging.indentation.scenario-stack>`.

    .. note::

        The fact that the :class:`ScenarioStack` class is a helper for the :class:`.scenariorunner.ScenarioRunner` one
        explains the definition of the additional methods and properties:

        - :meth:`checkcurrentscenario()`,
        - :attr:`current_step`,
        - :attr:`current_action_result`.

        By the way, this makes this class being a bit more than just a *scenario stack manager*,
        but rather a *scenario execution context manager*.

        Whatever, the name of this class is convenient as is,
        even though it is labelled as a "stack" only.
    """

    class ContextError(Exception):
        """
        Notifies a scenario stack error.
        """
        def __init__(self):  # type: (...) -> None
            """
            Defines the error message.
            """
            Exception.__init__(self, "Invalid scenario context")

    def __init__(self):  # type: (...) -> None
        """
        Initializes an empty scenario execution stack.
        """
        from .debugclasses import DebugClass
        from .logextradata import LogExtraData

        Logger.__init__(self, log_class=DebugClass.SCENARIO_STACK)
        self.setextraflag(LogExtraData.ACTION_RESULT_MARGIN, False)

        #: Instances under construction.
        self.building = BuildingContext()  # type: BuildingContext

        #: Scenario execution stack.
        #:
        #: The first item defines the :attr:`main_scenario`.
        #: The subscenarios (if any) then follow.
        self.__scenario_executions = []  # type: typing.List[ScenarioExecution]

        #: History of scenario executions.
        #:
        #: Main scenario executions only.
        #: In the chronological order.
        self.history = []  # type: typing.List[ScenarioExecution]

    def pushscenarioexecution(
            self,
            scenario_execution,  # type: ScenarioExecution
    ):  # type: (...) -> None
        """
        Adds a scenario execution instance in the scenario execution stack.

        :param scenario_execution: Scenario execution to set on top of the scenario execution stack.
        """
        self.debug("pushscenarioexecution(): Pushing scenario execution %r", scenario_execution)

        if not self.__scenario_executions:
            self.history.append(scenario_execution)
        self.__scenario_executions.append(scenario_execution)

    def popscenarioexecution(self):  # type: (...) -> ScenarioExecution
        """
        Removes the last scenario execution from the scenario execution stack.

        :return: Scenario execution removed.
        """
        self.debug("popscenarioexecution(): Popping scenario execution")

        assert self.__scenario_executions, "No more scenario execution in the scenario execution stack"
        _last_scenario_execution = self.__scenario_executions.pop(-1)  # type: ScenarioExecution
        return _last_scenario_execution

    @property
    def size(self):  # type: (...) -> int
        """
        Returns the size of the scenario execution stack.

        :return: Number of scenario executions currently stacked.
        """
        return len(self.__scenario_executions)

    @property
    def main_scenario_definition(self):  # type: (...) -> typing.Optional[ScenarioDefinition]
        """
        Main scenario definition under execution.

        Returns the reference of the top scenario definition under execution,
        whether subscenarios are being executed or not.

        Almost equivalent to :attr:`main_scenario_execution`, but retrieves the scenario definition instance.
        """
        if self.__scenario_executions:
            return self.__scenario_executions[0].definition
        return None

    @property
    def main_scenario_execution(self):  # type: (...) -> typing.Optional[ScenarioExecution]
        """
        Main scenario execution instance.

        Returns the reference of the top scenario execution instance,
        whether subscenarios are being executed or not.

        Almost equivalent to :attr:`main_scenario_definition`, but retrieves the scenario execution instance.
        """
        if self.__scenario_executions:
            return self.__scenario_executions[0]
        return None

    def ismainscenario(
            self,
            scenario,  # type: typing.Union[ScenarioDefinition, ScenarioExecution]
    ):  # type: (...) -> bool
        """
        Tells whether the given scenario corresponds to the main one under execution.

        :param scenario: Scenario definition or scenario execution to check.
        :return: ``True`` if the scenario corresponds to the main scenario, ``False`` otherwise.
        """
        _scenario_definition = None  # type: typing.Optional[ScenarioDefinition]
        if isinstance(scenario, ScenarioDefinition):
            _scenario_definition = scenario
        if isinstance(scenario, ScenarioExecution):
            _scenario_definition = scenario.definition
        if _scenario_definition and self.main_scenario_definition:
            if _scenario_definition is self.main_scenario_definition:
                return True
        return False

    @property
    def current_scenario_definition(self):  # type: (...) -> typing.Optional[ScenarioDefinition]
        """
        Current scenario definition under execution.

        The latest unterminated subscenario if any,
        i.e. the main scenario if no current sub-scenario.

        Almost equivalent to :attr:`current_scenario_execution`, but retrieves the scenario definition instance.
        """
        if self.__scenario_executions:
            return self.__scenario_executions[-1].definition
        return None

    @property
    def current_scenario_execution(self):  # type: (...) -> typing.Optional[ScenarioExecution]
        """
        Current scenario execution instance.

        The latest unterminated subscenario if any,
        i.e. the main scenario if no current sub-scenario.

        Almost equivalent to :attr:`current_scenario_definition`, but retrieves the scenario execution instance.
        """
        if self.__scenario_executions:
            return self.__scenario_executions[-1]
        return None

    def iscurrentscenario(
            self,
            scenario,  # type: typing.Union[ScenarioDefinition, ScenarioExecution]
    ):  # type: (...) -> bool
        """
        Tells whether the given scenario corresponds to the one on top of the scenario stack.

        :param scenario: Scenario definition or scenario execution to check.
        :return: ``True`` if the scenario corresponds to the main scenario, ``False`` otherwise.
        """
        _scenario_definition = None  # type: typing.Optional[ScenarioDefinition]
        if isinstance(scenario, ScenarioDefinition):
            _scenario_definition = scenario
        if isinstance(scenario, ScenarioExecution):
            _scenario_definition = scenario.definition
        if _scenario_definition and self.current_scenario_definition:
            if _scenario_definition is self.current_scenario_definition:
                return True
        return False

    @property
    def current_step_definition(self):  # type: (...) -> typing.Optional[StepDefinition]
        """
        Current step definition under execution.

        Out of the current scenario.

        Compared with :attr:`current_step_execution`,
        this method returns the step definition whatever the execution mode of the :class:`.scenariorunner.ScenarioRunner`.

        ``None`` if no current step definition under execution.
        """
        if self.current_scenario_execution:
            return self.current_scenario_execution.current_step_definition
        return None

    @property
    def current_step_execution(self):  # type: (...) -> typing.Optional[StepExecution]
        """
        Current step execution instance.

        Out of the :attr:`current_step`.

        Compared with :attr:`current_step_definition`,
        this method may not return a step execution instance when the :class:`.scenariorunner.ScenarioRunner` is building objects.

        ``None`` if no current step execution instance.
        """
        if self.current_step_definition and self.current_step_definition.executions:
            return self.current_step_definition.executions[-1]
        return None

    @property
    def current_action_result_definition(self):  # type: (...) -> typing.Optional[ActionResultDefinition]
        """
        Current action or expected result definition under execution.

        Out of the current step definition or step execution.

        ``None`` current action / expected result definition.
        """
        if self.current_step_execution:
            return self.current_step_execution.current_action_result_definition
        elif self.current_step_definition and self.current_step_definition.actions_results:
            return self.current_step_definition.actions_results[-1]
        return None

    @property
    def current_action_result_execution(self):  # type: (...) -> typing.Optional[ActionResultExecution]
        """
        Current action or expected result execution instance.

        Out of the current step execution.

        ``None`` if no current action / expected result execution instance.
        """
        if self.current_action_result_definition and self.current_action_result_definition.executions:
            return self.current_action_result_definition.executions[-1]
        return None

    @typing.overload
    def knownissue(
            self,
            __id,  # type: str
            __message,  # type: str
    ):  # type: (...) -> None
        """
        Deprecated.

        See :meth:`.stepuserapi.StepUserApi.knownissue()`.
        """

    @typing.overload
    def knownissue(
            self,
            message,  # type: str
            level=None,  # type: AnyIssueLevelType
            id=None,  # type: str  # noqa  ## Shadows built-in name 'id'
    ):  # type: (...) -> None
        """
        See :meth:`.stepuserapi.StepUserApi.knownissue()`.
        """

    def knownissue(
            self,
            *args,  # type: str
            **kwargs,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Registers a known issue in the current context.
        """
        _step_user_api = (
                self.current_step_definition
                or self.building.step_definition
                or self.current_scenario_definition
                or self.building.scenario_definition
        )  # type: typing.Optional[typing.Union[ScenarioDefinition, StepDefinition]]
        assert _step_user_api
        _step_user_api.knownissue(*args, **kwargs)

    def raisecontexterror(
            self,
            error_message,  # type: str
    ):  # type: (...) -> typing.NoReturn
        """
        Raises an error about the scenario stack execution.

        Displays error information about the current status of the stack for investigation purpose.

        :param error_message: Error message.
        :raise ScenarioStack.ContextError: Systematically.
        """
        self.error("")
        self.error(f"Invalid scenario context: {error_message}")
        self.error("")
        self.error("Building context:")
        self.error(f"- scenario definition = {self.building.scenario_definition!r}")
        self.error(f"- step definition = {self.building.step_definition!r}")
        self.error("Execution stack:")
        self.error(f"- main scenario: definition = {self.main_scenario_definition!r}, execution = {self.main_scenario_execution!r}")
        self.error(f"- current scenario: definition = {self.current_scenario_definition!r}, execution = {self.current_scenario_execution!r}")
        self.error(f"- current step: definition = {self.current_step_definition!r}, execution = {self.current_step_execution!r}")
        self.error(f"- current action/result: definition = {self.current_action_result_definition!r}, execution = {self.current_action_result_execution!r}")
        self.error("")
        raise ScenarioStack.ContextError()


__doc__ += """
.. py:attribute:: SCENARIO_STACK

    Main instance of :class:`ScenarioStack`.
"""
SCENARIO_STACK = ScenarioStack()  # type: ScenarioStack
