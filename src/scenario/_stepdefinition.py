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
Step definition.
"""

import inspect
import types
import typing

from ._assertions import Assertions  # `Assertions` used for inheritance.
from ._logger import Logger  # `Logger` used for inheritance.
from ._stepuserapi import StepUserApi  # `StepUserApi` used for inheritance.

if typing.TYPE_CHECKING:
    from ._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from ._knownissues import KnownIssue as _KnownIssueType


class StepDefinition(StepUserApi, Assertions, Logger):
    """
    Step definition management.
    """

    @classmethod
    def getinstance(
            cls,  # type: typing.Type[VarStepDefinitionType]
            index=None,  # type: int
    ):  # type: (...) -> VarStepDefinitionType
        """
        Expects and retrieves a step with its appropriate type.

        :param index: Optional step index of the kind. See :meth:`._scenariodefinition.ScenarioDefinition.getstep()` for more details.
        :return: The expected step for the current scenario, typed with the final user step definition class this method is called onto.

        The "current" scenario is actually the one being executed or built.

        Makes it possible to easily access the attributes and methods defined with a user step definition.
        """
        from ._reflection import qualname
        from ._scenariostack import SCENARIO_STACK
        if typing.TYPE_CHECKING:
            from ._stepspecifications import AnyStepDefinitionSpecificationType

        def _ensurereturntype(step_definition):  # type: (StepDefinition) -> VarStepDefinitionType
            """
            Avoids using ``# type: ignore`` pragmas every time this :meth:`StepDefinition.getinstance()` method returns a value.
            """
            _step_definition = typing.cast(typing.Any, step_definition)  # type: VarStepDefinitionType  # noqa  ## Shadows name '_step_definition' from outer scope
            return _step_definition

        _step_specification = cls if (index is None) else (cls, index)  # type: AnyStepDefinitionSpecificationType
        if SCENARIO_STACK.building.scenario_definition:
            _step_definition = SCENARIO_STACK.building.scenario_definition.getstep(_step_specification)  # type: typing.Optional[StepDefinition]
            if _step_definition is not None:
                return _ensurereturntype(_step_definition)
        if SCENARIO_STACK.current_scenario_definition:
            _step_definition = SCENARIO_STACK.current_scenario_definition.getstep(_step_specification)  # Type already defined above.
            if _step_definition is not None:
                return _ensurereturntype(_step_definition)
        if not (SCENARIO_STACK.building.scenario_definition or SCENARIO_STACK.current_scenario_definition):
            SCENARIO_STACK.raisecontexterror("No current scenario definition")
        else:
            SCENARIO_STACK.raisecontexterror(f"No such step definition of type {qualname(cls)}")

    def __init__(
            self,
            method=None,  # type: typing.Optional[types.MethodType]
    ):  # type: (...) -> None
        """
        :param method: Method that defines the step, when applicable. Optional.
        """
        from ._locations import CodeLocation
        from ._scenariodefinition import ScenarioDefinition
        from ._stepexecution import StepExecution

        #: Owner scenario.
        #:
        #: Initially set with a void reference.
        #: Fixed when :meth:`._scenariodefinition.ScenarioDefinition.addstep()` is called.
        self.scenario = ScenarioDefinition.__new__(ScenarioDefinition)  # type: ScenarioDefinition

        #: Step method, if any.
        self.method = method  # type: typing.Optional[types.MethodType]

        #: Definition location.
        self.location = CodeLocation.fromclass(type(self))  # type: CodeLocation
        if self.method:
            self.location = CodeLocation.frommethod(self.method)

        StepUserApi.__init__(self)
        Assertions.__init__(self)
        Logger.__init__(self, log_class=self.name)

        # Activate debugging by default for step definitions.
        self.enabledebug(True)

        #: Step description.
        self.description = None  # type: typing.Optional[str]
        #: List of actions and expected results that define the step.
        self.__action_result_definitions = []  # type: typing.List[_ActionResultDefinitionType]

        #: Step executions.
        self.executions = []  # type: typing.List[StepExecution]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflection import qualname

        if type(self) is StepDefinition:
            return f"<{qualname(type(self))} {self.name!r}>"
        else:
            return f"<{qualname(type(self))}#{self.number}>"

    def __str__(self):  # type: () -> str
        """
        Returns a human readable representation of the step definition.
        """
        return f"step#{self.number} ({self.name})"

    @property
    def name(self):  # type: () -> str
        """
        Step name, i.e. the fully qualified name of the class or method defining it.
        """
        return self.location.qualname

    @property
    def number(self):  # type: () -> int
        """
        Step definition number.

        Number of this step definition within the steps defining the related scenario.
        Starting from 1, as displayed to the user.
        """
        from ._stepsection import StepSectionDescription

        _step_number = 0  # type: int
        # Check the :attr:`scenario` attribute has been set with a real object.
        if hasattr(self.scenario, "name"):
            for _step_definition in self.scenario.steps:  # type: StepDefinition
                # Skip section steps.
                if isinstance(_step_definition, StepSectionDescription):
                    continue

                _step_number += 1
                if _step_definition is self:
                    break
        return _step_number

    def addactionresult(
            self,
            *action_result_definitions  # type: _ActionResultDefinitionType
    ):  # type: (...) -> StepDefinition
        """
        Adds actions / expected results to the list defining the step.

        :param action_result_definitions: Action / expected result definitions to add.
        :return: ``self``
        """
        for _action_result_definition in action_result_definitions:  # type: _ActionResultDefinitionType
            _action_result_definition.step = self
            self.__action_result_definitions.append(_action_result_definition)
        return self

    @property
    def actions_results(self):  # type: () -> typing.List[_ActionResultDefinitionType]
        """
        Action / expected result list.
        """
        return self.__action_result_definitions.copy()

    def getactionresult(
            self,
            index,  # type: int
    ):  # type: (...) -> _ActionResultDefinitionType
        """
        Retrieves an :class:`._actionresultdefinition.ActionResultDefinition` instance from its location.

        :param index: Action/result definition index.
        :return: Action/result definition instance.
        """
        return self.__action_result_definitions[index]

    def step(self):  # type: (...) -> None
        """
        Calls :attr:`method`, when not overloaded.

        This method should be overloaded by user step definition classes.

        Otherwise, this base implementation of this method expects the :attr:`method` attribute to be set, and invokes it.
        """
        from ._scenariorunner import SCENARIO_RUNNER

        assert self.method is not None, f"{self} not implemented"
        SCENARIO_RUNNER.debug("Invoking %r", self.method)
        self.method()


if typing.TYPE_CHECKING:
    #: Variable step definition type.
    VarStepDefinitionType = typing.TypeVar("VarStepDefinitionType", bound=StepDefinition)


class StepDefinitionHelper:
    """
    Step definition helper methods.

    Avoids the public exposition of methods for internal implementation only.
    """

    def __init__(
            self,
            definition,  # type: StepDefinition
    ):  # type: (...) -> None
        """
        Instanciates a helper for the given step definition.

        :param definition: Step definition instance this helper works for.
        """
        #: Step definition instance this helper works for.
        self.definition = definition

    def saveinitknownissues(self):  # type: (...) -> None
        """
        Saves *init* known issues for the related step definition.

        I.e. the known issues declared at the definition level, before the :meth:StepDefinition.step()` method has been called.

        The appropriate call to this method is made in :meth:`._scenariorunner.ScenarioRunner._buildscenario()`.
        """
        # Save a copy of the curent `ScenarioDefinition.known_issues` list in a hidden field.
        setattr(self.definition, "__init_known_issues", list(self.definition.known_issues))

    def getinitknownissues(self):  # type: (...) -> typing.Sequence[_KnownIssueType]
        """
        Retrieves the known issue list saved by :meth:`saveinitknownissues()` for the related step definition.

        :return: *Init* known issue list.
        """
        if hasattr(self.definition, "__init_known_issues"):
            _init_known_issues = getattr(self.definition, "__init_known_issues")  # type: typing.Any
            if isinstance(_init_known_issues, list):
                return _init_known_issues
        return []


class StepMethods:
    """
    Collection of static methods to help manipulating step methods.
    """

    @staticmethod
    def _hierarchycount(
            logger,  # type: Logger
            method,  # type: types.MethodType
    ):  # type: (...) -> int
        """
        Returns the number of classes in class hierarchy that have this method being declared.

        :param logger: Logger to use for debugging.
        :param method: Method to look for accessibility in class hierarchy.
        :return: Count. The higher, the upper class the method is defined into.

        Used by the :meth:`sortbyhierarchythennames()` and :meth:`sortbyreversehierarchythennames()` methods.
        """
        from ._reflection import qualname

        _count = 0  # type: int
        for _cls in inspect.getmro(method.__self__.__class__):  # type: type
            for _method_name, _method in inspect.getmembers(_cls, predicate=inspect.isfunction):  # type: str, types.MethodType
                if _method_name == method.__name__:
                    _count += 1

        logger.debug("StepMethods._hierarchycount(%s) -> %d", qualname(method), _count)
        return _count

    @staticmethod
    def _dispmethodlist(
            methods,  # type: typing.List[types.MethodType]
    ):  # type: (...) -> str
        """
        Computes a debug representation of a method list.

        :param methods: Array of methods to debug.
        :return: Debug representation.
        """
        from ._reflection import qualname

        return f"[{', '.join(qualname(_method) for _method in methods)}]"

    @staticmethod
    def sortbynames(
            logger,  # type: Logger
            methods,  # type: typing.List[types.MethodType]
    ):  # type: (...) -> None
        """
        Sorts an array of methods by method names.

        :param logger: Logger to use for debugging.
        :param methods: Array of methods to sort.
        """
        logger.debug("StepMethods.sortbynames(%s)", StepMethods._dispmethodlist(methods))
        methods.sort(key=lambda method: method.__name__)
        logger.debug("                     -> %s", StepMethods._dispmethodlist(methods))

    @staticmethod
    def sortbyhierarchythennames(
            logger,  # type: Logger
            methods,  # type: typing.List[types.MethodType]
    ):  # type: (...) -> None
        """
        Sorts an array of methods by hierarchy at first, then by method names.

        :param logger: Logger to use for debugging.
        :param methods: Array of methods to sort.

        Makes the methods defined in the higher classes be executed prior to those defined in the lower classes,
        i.e. makes the most specific methods be executed at last.

        Formerly used by *before-test* and *before-step* steps.
        """
        logger.debug("StepMethods.sortbyhierarchythennames(%s)", StepMethods._dispmethodlist(methods))
        # We want to execute the higher class methods at first.
        # When a method is defined in an upper class, its hierarchy count is high.
        # Let's negate the result of :meth:`StepMethods._hierarchycount()` in order to sort the higher class methods at the beginning of the list.
        methods.sort(key=lambda method: (- StepMethods._hierarchycount(logger, method), method.__name__))
        logger.debug("                                  -> %s", StepMethods._dispmethodlist(methods))

    @staticmethod
    def sortbyreversehierarchythennames(
            logger,  # type: Logger
            methods,  # type: typing.List[types.MethodType]
    ):  # type: (...) -> None
        """
        Sorts an array of methods by reverse hierarchy first, then by method names.

        :param logger: Logger to use for debugging.
        :param methods: Array of methods to sort.

        Makes the methods defined in the lower classes be executed prior to those defined in the upper classes,
        i.e. makes the most specific methods be executed at first.

        Formerly used by *after-test* and *after-step* steps.
        """
        logger.debug("StepMethods.sortbyreversehierarchythennames(%s)", StepMethods._dispmethodlist(methods))
        # We want to execute the lower class methods at first.
        # When a method is defined in a lower class, its hierarchy count is low.
        # Do not negate the result of :meth:`StepMethods._hierarchycount()` in order to sort the lower class methods at the beginning of the list.
        methods.sort(key=lambda method: (StepMethods._hierarchycount(logger, method), method.__name__))
        logger.debug("                                         -> %s", StepMethods._dispmethodlist(methods))
