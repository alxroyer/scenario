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
Step definition.
"""

import inspect
import types
import typing

# `ActionResultDefinition` used in method signatures.
from .actionresultdefinition import ActionResultDefinition
# `Assertions` used for inheritance.
from .assertions import Assertions
# `CodeLocation` used in method signatures.
from .locations import CodeLocation
# `Logger` used for inheritance.
from .logger import Logger
# `StepUserApi` used for inheritance.
from .stepuserapi import StepUserApi


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

        :param index: Optional step index of the kind. Optional. See :meth:`.scenariodefinition.ScenarioDefinition.getstep()` for more details.
        :return: The expected step for the current scenario, typed with the final user step definition class this method is called onto.

        The "current" scenario is actually the one being executed or built.

        Makes it possible to easily access the attributes and methods defined with a user step definition.
        """
        from .scenariostack import SCENARIO_STACK

        if SCENARIO_STACK.building.scenario_definition:
            _step_definition = SCENARIO_STACK.building.scenario_definition.getstep(cls, index)  # type: typing.Optional[StepDefinition]
            if _step_definition is not None:
                return _step_definition  # type: ignore  ## Incompatible return value type (got "StepDefinition", expected "VarStepDefinitionType")
        if SCENARIO_STACK.current_scenario_definition:
            _step_definition = SCENARIO_STACK.current_scenario_definition.getstep(cls, index)  # Type already defined above.
            if _step_definition is not None:
                return _step_definition  # type: ignore  ## Incompatible return value type (got "StepDefinition", expected "VarStepDefinitionType")
        if not (SCENARIO_STACK.building.scenario_definition or SCENARIO_STACK.current_scenario_definition):
            SCENARIO_STACK.raisecontexterror("No current scenario definition")
        else:
            SCENARIO_STACK.raisecontexterror("No such step definition of type %s" % cls.__name__)

    def __init__(
            self,
            method=None,  # type: typing.Optional[types.MethodType]
    ):  # type: (...) -> None
        """
        :param method: Method that defines the step, when applicable. Optional.
        """
        from .scenariodefinition import ScenarioDefinition
        from .stepexecution import StepExecution

        #: Owner scenario.
        #:
        #: Initially set with a void reference.
        #: Fixed when :meth:`.scenariodefinition.ScenarioDefinition.addsteps()` is called.
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
        self.__action_result_definitions = []  # type: typing.List[ActionResultDefinition]

        #: Step executions.
        self.executions = []  # type: typing.List[StepExecution]

    def __repr__(self):  # type: (...) -> str
        """
        Canonical string representation.
        """
        from .reflex import qualname

        if type(self) is StepDefinition:
            return "<%s '%s'>" % (qualname(type(self)), self.name)
        else:
            return "<%s#%d>" % (qualname(type(self)), self.number)

    def __str__(self):  # type: (...) -> str
        """
        Returns a human readable representation of the step definition.
        """
        return self.name

    @property
    def name(self):  # type: (...) -> str
        """
        Step name, i.e. the fully qualified name of the class or method defining it.
        """
        return self.location.qualname

    @property
    def number(self):  # type: (...) -> int
        """
        Step definition number.

        Number of this step definition within the steps defining the related scenario.
        Starting from 1, as displayed to the user.
        """
        _step_number = 0  # type: int
        # Check the :attr:`scenario` attribute has been set with a real object.
        if hasattr(self.scenario, "name"):
            for _step_definition in self.scenario.steps:  # type: StepDefinition
                _step_number += 1
                if _step_definition is self:
                    break
        return _step_number

    def addactionresult(
            self,
            *action_result_definitions  # type: ActionResultDefinition
    ):  # type: (...) -> StepDefinition
        """
        Adds actions / expected results to the list defining the step.

        :param action_result_definitions: Action / expected result definitions to add.
        :return: ``self``
        """
        for _action_result_definition in action_result_definitions:  # type: ActionResultDefinition
            _action_result_definition.step = self
            self.__action_result_definitions.append(_action_result_definition)
        return self

    @property
    def actions_results(self):  # type: (...) -> typing.List[ActionResultDefinition]
        """
        Action / expected result list.
        """
        return self.__action_result_definitions.copy()

    def getactionresult(
            self,
            location,  # type: CodeLocation
    ):  # type: (...) -> typing.Optional[ActionResultDefinition]
        """
        Retrieves an :class:`.actionresultdefinition.ActionResultDefinition` instance from its location.

        :param location: Location of the action or expected result.
        :return: :class:`.actionresultdefinition.ActionResultDefinition` instance, if found.
        """
        for _action_result_definition in self.__action_result_definitions:  # type: ActionResultDefinition
            if _action_result_definition.location and (_action_result_definition.location.tolongstring() == location.tolongstring()):
                return _action_result_definition
        return None

    def step(self):  # type: (...) -> None
        """
        Calls :attr:`method`, when not overloaded.

        This method should be overloaded by user step definition classes.

        Otherwise, this base implementation of this method expects the :attr:`method` attribute to be set, and invokes it.
        """
        from .scenariorunner import SCENARIO_RUNNER

        assert self.method is not None, "%s not implemented" % str(self).capitalize()
        SCENARIO_RUNNER.debug("Invoking %s" % repr(self.method))
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
        self.definition = definition

    def matchspecification(
            self,
            step_specification,  # type: StepSpecificationType
    ):  # type: (...) -> bool
        """
        Determines whether the given step specification matches the related step definition.

        :param step_specification: Step specification to check.
        :return: :const:`True` when the specification matches the related step definition.
        """
        if isinstance(step_specification, StepDefinition):
            if step_specification is self.definition:
                return True
        if isinstance(step_specification, int):
            if self.definition.number == step_specification:
                return True
        if isinstance(step_specification, str):
            if str(self.definition).endswith(step_specification):
                return True
        if isinstance(step_specification, type):
            if isinstance(self.definition, step_specification):
                return True
        return False

    @staticmethod
    def specificationdescription(
            step_specification,  # type: typing.Optional[StepSpecificationType]
    ):  # type: (...) -> str
        """
        Returns a human readable representation of the step specification.

        :param step_specification: Step specification to compute a string representation for.
        :return: String representation.
        """
        if isinstance(step_specification, StepDefinition):
            return "[instance is %s]" % str(step_specification)
        if isinstance(step_specification, str):
            return "[%s]" % repr(step_specification)
        if isinstance(step_specification, type):
            return "[class is %s]" % step_specification.__name__
        return repr(step_specification)


class StepMethods:
    """
    Collection of static methods to help manipulating methods.
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
        from .reflex import qualname

        _count = 0  # type: int
        for _cls in inspect.getmro(method.__self__.__class__):  # type: type
            for _method_name, _method in inspect.getmembers(_cls, predicate=inspect.isfunction):  # type: str, types.MethodType
                if _method_name == method.__name__:
                    _count += 1

        logger.debug("StepMethods._hierarchycount(%s) -> %d" % (qualname(method), _count))
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
        from .reflex import qualname

        return "[%s]" % ", ".join(qualname(_method) for _method in methods)

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
        logger.debug("StepMethods.sortbynames(%s)" % StepMethods._dispmethodlist(methods))
        methods.sort(key=lambda method: method.__name__)
        logger.debug("                     -> %s" % StepMethods._dispmethodlist(methods))

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
        logger.debug("StepMethods.sortbyhierarchythennames(%s)" % StepMethods._dispmethodlist(methods))
        # We want to execute the higher class methods at first.
        # When a method is defined in an upper class, its hierarchy count is high.
        # Let's negate the result of :meth:`StepMethods._hierarchycount()` in order to sort the higher class methods at the beginning of the list.
        methods.sort(key=lambda method: (- StepMethods._hierarchycount(logger, method), method.__name__))
        logger.debug("                                  -> %s" % StepMethods._dispmethodlist(methods))

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
        logger.debug("StepMethods.sortbyreversehierarchythennames(%s)" % StepMethods._dispmethodlist(methods))
        # We want to execute the lower class methods at first.
        # When a method is defined in a lower class, its hierarchy count is low.
        # Do not negate the result of :meth:`StepMethods._hierarchycount()` in order to sort the lower class methods at the beginning of the list.
        methods.sort(key=lambda method: (StepMethods._hierarchycount(logger, method), method.__name__))
        logger.debug("                                         -> %s" % StepMethods._dispmethodlist(methods))


if typing.TYPE_CHECKING:
    #: Step specification.
    #:
    #: Either:
    #: 1. a step definition instance directly,
    #: 2. or a step definition class,
    #: 3. a string representation, being the qualified name of the class or method (right part),
    #: 4. an integer specifying the step definition number in its scenario.
    #:
    #: The :meth:`StepDefinitionHelper.matchspecification()` checks whether a step definition matches such step specification.
    StepSpecificationType = typing.Union[StepDefinition, typing.Type[StepDefinition], str, int]
