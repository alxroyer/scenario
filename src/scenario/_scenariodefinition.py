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
Scenario definition.
"""

import abc
import enum
import inspect
import types
import typing

from ._assertions import Assertions  # `Assertions` used for inheritance.
from ._logger import Logger  # `Logger` used for inheritance.
from ._stepuserapi import StepUserApi  # `StepUserApi` used for inheritance.

if typing.TYPE_CHECKING:
    from ._path import AnyPathType
    from ._stepdefinition import StepDefinition as _StepDefinitionType, StepSpecificationType, VarStepDefinitionType
    from ._stepsection import StepSectionDescription as _StepSectionDescriptionType


class MetaScenarioDefinition(abc.ABCMeta):
    """
    Meta-class for :class:`ScenarioDefinition`.

    So that it can be a meta-class for :class:`ScenarioDefinition`,
    :class:`MetaScenarioDefinition` must inherit from ``abc.ABCMeta`` (which makes it inherit from ``type`` by the way)
    because the :class:`._stepuserapi.StepUserApi` base class inherits from ``abc.ABC``.
    """

    def __new__(
            mcs,
            name,  # type: str
            bases,  # type: typing.Tuple[type, ...]
            attrs,  # type: typing.Dict[str, typing.Any]
            **kwargs  # type: typing.Any
    ):  # type: (...) -> typing.Any
        """
        Overloads class definition of :class:`ScenarioDefinition` class and sub-classes.

        Sets :class:`MetaScenarioDefinition.InitWrapper` instances in place of ``__init__()`` methods,
        in order to have :class:`ScenarioDefinition` initializers enclosed with
        :meth:`._scenariostack.BuildingContext.pushscenariodefinition()` / :meth:`._scenariostack.BuildingContext.popscenariodefinition()` calls.

        :param name: New class name.
        :param bases: Base classes for the new class.
        :param attrs: New class attributes and methods.
        :param kwargs: Optional arguments.
        """
        attrs = attrs.copy()
        if "__init__" in attrs:
            attrs["__init__"] = MetaScenarioDefinition.InitWrapper(attrs["__init__"])
        return type.__new__(mcs, name, bases, attrs, **kwargs)

    class InitWrapper:
        """
        Wrapper for ``__init__()`` methods of :class:`ScenarioDefinition` instances.

        Encloses the initializer's execution with
        :meth:`._scenariostack.BuildingContext.pushscenariodefinition()` / :meth:`._scenariostack.BuildingContext.popscenariodefinition()` calls,
        so that the building context of scenario stack knows about the scenario definition being built.
        """

        def __init__(
                self,
                init_method,  # type: types.FunctionType
        ):  # type: (...) -> None
            """
            Stores the original ``__init__()`` method.

            :param init_method: Original ``__init__()`` method.
            """
            # Note: `mypy` (as of 0.910) seems to mess up between `types.FunctionType` and `types.MethodType`
            #       when assigning the `init_method` member variable below.
            #       Let's use `typing.cast(Any)` to work around it.

            #: Original ``__init__()`` method.
            self.init_method = typing.cast(typing.Any, init_method)  # type: types.FunctionType

        def __get__(
                self,
                obj,  # type: typing.Any
                objtype=None,  # type: type
        ):  # type: (...) -> types.MethodType
            """
            Wrapper descriptor: returns a ``__init__()`` bound method with ``obj``.

            :param obj: Optional instance reference.
            :param objtype: Unused.
            :return: Bound initializer callable (as long as ``obj`` is not ``None``).

            Inspired from:

            - https://docs.python.org/3/howto/descriptor.html
            - https://github.com/dabeaz/python-cookbook/blob/master/src/9/multiple_dispatch_with_function_annotations/example1.py
            """
            if obj is not None:
                return types.MethodType(self, obj)
            else:
                return self  # type: ignore[return-value]  ## "InitWrapper", expected "MethodType"

        def __call__(
                self,
                *args,  # type: typing.Any
                **kwargs  # type: typing.Any
        ):  # type: (...) -> None
            """
            ``__init__()`` wrapper call.

            :param args:
                Positional arguments.

                First item should normally be the :class:`ScenarioDefinition` instance the initializer is executed for.
            :param kwargs:
                Named arguments.

            Pushes the scenario definition to the building context of the scenario stack before the initializer's execution,
            then removes it out after the initializer's execution.
            """
            from ._scenariostack import SCENARIO_STACK

            _scenario_definition = None  # type: typing.Optional[ScenarioDefinition]
            if (len(args) >= 1) and isinstance(args[0], ScenarioDefinition):
                _scenario_definition = args[0]

            # Push the scenario definition to the building context of the scenario stack.
            if _scenario_definition:
                SCENARIO_STACK.debug("MetaScenarioDefinition.InitWrapper.__call__(): Pushing scenario being built")
                SCENARIO_STACK.building.pushscenariodefinition(_scenario_definition)

            # Call the original ``__init__()`` method.
            self.init_method(*args, **kwargs)

            # Pop the scenario definition from the building context of the scenario stack.
            if _scenario_definition:
                SCENARIO_STACK.debug("MetaScenarioDefinition.InitWrapper.__call__(): Popping scenario being built")
                SCENARIO_STACK.building.popscenariodefinition(_scenario_definition)


class ScenarioDefinition(StepUserApi, Assertions, Logger, metaclass=MetaScenarioDefinition):
    """
    Base class for any final test scenario.

    See the :ref:`quickstart guide <quickstart>`.
    """

    @classmethod
    def getinstance(
            cls,  # type: typing.Type[VarScenarioDefinitionType]
    ):  # type: (...) -> VarScenarioDefinitionType
        """
        Expects and retrieves the current scenario definition with its appropriate type.

        :return: The current scenario definition instance, typed with the final user scenario definition class this method is called onto.

        The "current" scenario is actually the one being executed or built.

        Makes it possible to easily access the attributes and methods defined with a user scenario definition.
        """
        from ._reflex import qualname
        from ._scenariostack import SCENARIO_STACK

        if isinstance(SCENARIO_STACK.building.scenario_definition, cls):
            return SCENARIO_STACK.building.scenario_definition
        if isinstance(SCENARIO_STACK.current_scenario_definition, cls):
            return SCENARIO_STACK.current_scenario_definition
        SCENARIO_STACK.raisecontexterror(f"Current scenario definition not of type {qualname(cls)}")

    def __init__(self):  # type: (...) -> None
        """
        Activates debugging by default.

        Determines the scenario name and *log class* by the way from the scenario script path.
        """
        from ._locations import CodeLocation
        from ._path import Path
        from ._scenarioexecution import ScenarioExecution

        #: Definition location.
        self.location = CodeLocation.fromclass(type(self))  # type: CodeLocation

        #: Script path.
        self.script_path = Path(self.location.file)  # type: Path

        #: Scenario name: i.e. script pretty path.
        self.name = self.script_path.prettypath  # type: str

        StepUserApi.__init__(self)
        Assertions.__init__(self)
        Logger.__init__(self, log_class=self.name)

        # Activate debugging by default for scenario definitions.
        self.enabledebug(True)

        #: Continue on error option.
        #:
        #: Local configuration for the current scenario.
        #:
        #: Prevails on :attr:`._scenarioconfig.ScenarioConfig.Key.CONTINUE_ON_ERROR`
        #: (see :meth:`._scenariorunner.ScenarioRunner._shouldstop()`).
        #:
        #: Not set by default.
        self.continue_on_error = None  # type: typing.Optional[bool]

        #: Scenario attributes (see :meth:`._scenarioconfig.ScenarioConfig.expectedscenarioattributes()`).
        self.__attributes = {}  # type: typing.Dict[str, typing.Any]

        #: List of steps that define the scenario.
        self.__step_definitions = []  # type: typing.List[_StepDefinitionType]

        #: Scenario execution, if any.
        self.execution = None  # type: typing.Optional[ScenarioExecution]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        from ._reflex import qualname

        # Sometimes, `__repr__()` may be called on an object being built.
        if hasattr(self, "name"):
            return f"<{qualname(type(self))} {self.name!r}>"
        else:
            return super().__repr__()

    def __str__(self):  # type: () -> str
        """
        Human readable string representation of the scenario definition.
        """
        return self.name

    def setattribute(
            self,
            name,  # type: typing.Union[str, enum.Enum]
            value,  # type: typing.Any
    ):  # type: (...) -> ScenarioDefinition
        """
        Defines an attribute for the scenario.

        :param name: Attribute name.
        :param value: Attribute value.
        :return: ``self``
        """
        from ._enumutils import enum2str

        self.__attributes[enum2str(name)] = value
        return self

    def getattribute(
            self,
            name,  # type: typing.Union[str, enum.Enum]
    ):  # type: (...) -> typing.Any
        """
        Retrieves an attribute value defined with the scenario.

        :param name: Attribute name.
        :return: Attribute value.
        :raise KeyError: When the attribute name is not defined.
        """
        from ._enumutils import enum2str

        return self.__attributes[enum2str(name)]

    def getattributenames(self):  # type: (...) -> typing.List[str]
        """
        Retrieves all attribute names defined with the scenario.

        :return: List of attribute names, sorted in alphabetical order.
        """
        return sorted([_name for _name in self.__attributes])

    def section(
            self,
            description,  # type: str
    ):  # type: (...) -> _StepSectionDescriptionType
        """
        Adds a step section description.

        :param description: Description for the section.
        :return: The step section description step just added.
        """
        from ._stepsection import StepSectionDescription

        _step_section_description = StepSectionDescription(description)  # type: StepSectionDescription
        _step_section_description.scenario = self
        self.__step_definitions.append(_step_section_description)
        return _step_section_description

    def addstep(
            self,
            step_definition,  # type: VarStepDefinitionType
    ):  # type: (...) -> VarStepDefinitionType
        """
        Adds steps to the step list defining the scenario.

        :param step_definition: Step definition to add.
        :return: The step just added.
        """
        step_definition.scenario = self
        self.__step_definitions.append(step_definition)
        return step_definition

    def getstep(
            self,
            step_specification=None,  # type: StepSpecificationType
            index=None,  # type: int
    ):  # type: (...) -> typing.Optional[_StepDefinitionType]
        """
        Finds a step definition.

        :param step_specification: Step specification (see :attr:`._stepdefinition.StepSpecificationType`), or ``None``.
        :param index: Step index in the matching list. Last item when not specified.
        :return: Step definition found, if any.
        """
        from ._stepdefinition import StepDefinitionHelper

        _matching_step_definitions = []  # type: typing.List[_StepDefinitionType]
        for _step_definition in self.__step_definitions:  # type: _StepDefinitionType
            if step_specification is None:
                _matching_step_definitions.append(_step_definition)
            elif StepDefinitionHelper(_step_definition).matchspecification(step_specification):
                _matching_step_definitions.append(_step_definition)

        try:
            if index is None:
                index = -1
            return _matching_step_definitions[index]
        except IndexError:
            # Default to None.
            return None

    def expectstep(
            self,
            step_specification=None,  # type: StepSpecificationType
            index=None,  # type: int
    ):  # type: (...) -> _StepDefinitionType
        """
        Expects a step definition.

        When the step cannot be found, an exception is raised.

        :param step_specification: Step specification (see :attr:`._stepdefinition.StepSpecificationType`), or ``None``.
        :param index: Step index in the matching list. Last item when not specified.
        :return: Expected step.
        :raise KeyError: When the step definition could not be found.
        """
        from ._stepdefinition import StepDefinitionHelper

        _step_definition = self.getstep(step_specification, index)  # type: typing.Optional[_StepDefinitionType]
        if _step_definition is None:
            raise KeyError(f"No such step {StepDefinitionHelper.specificationdescription(step_specification)} (index: {index!r})")
        return _step_definition

    @property
    def steps(self):  # type: () -> typing.List[_StepDefinitionType]
        """
        Step list.
        """
        return self.__step_definitions.copy()


if typing.TYPE_CHECKING:
    #: Variable scenario definition type.
    VarScenarioDefinitionType = typing.TypeVar("VarScenarioDefinitionType", bound=ScenarioDefinition)


class ScenarioDefinitionHelper:
    """
    Scenario definition helper methods.

    Avoids the public exposition of methods for internal implementation only.
    """

    @staticmethod
    def getscenariodefinitionclassfromscript(
            script_path,  # type: AnyPathType
    ):  # type: (...) -> typing.Type[ScenarioDefinition]
        """
        Retrieves the scenario definitions classes from a Python script.

        :param script_path: Path of a Python script.
        :return: Scenario definition classes, if any.
        """
        from ._path import Path
        from ._reflex import importmodulefrompath

        # Load the test scenario module.
        script_path = Path(script_path)
        _module = importmodulefrompath(script_path)  # type: types.ModuleType

        # Find out the scenario classes in that module.
        _scenario_definition_class = None  # type: typing.Optional[typing.Type[ScenarioDefinition]]
        for _member_name, _member in inspect.getmembers(_module):  # type: str, typing.Any
            if inspect.isclass(_member) and issubclass(_member, ScenarioDefinition):
                # Don't select Scenarios from other modules (may occur when executing subscenarios)
                if _member.__module__ == _module.__name__:
                    _scenario_definition_class = _member

        if _scenario_definition_class is None:
            raise LookupError(f"Could not find scenario class in '{script_path}'")
        return _scenario_definition_class

    def __init__(
            self,
            definition,  # type: ScenarioDefinition
    ):  # type: (...) -> None
        """
        Instanciates a helper for the given scenario definition.

        :param definition: Scenario definition instance this helper works for.
        """
        from ._scenariorunner import SCENARIO_RUNNER

        #: Related scenario definition.
        self.definition = definition  # type: ScenarioDefinition

        #: Make this class log as if it was part of the :class:`._scenariorunner.ScenarioRunner` execution.
        self._logger = SCENARIO_RUNNER  # type: Logger

    def buildsteps(self):  # type: (...) -> None
        """
        Reads the scenario step list by inspecting the user scenario class,
        and feeds the scenario definition step list.
        """
        from ._reflex import qualname
        from ._stepdefinition import StepDefinition, StepMethods

        # Scan methods.
        _methods = []  # type: typing.List[types.MethodType]
        self._logger.debug("Searching for steps in %s:", qualname(type(self.definition)))
        for _method_name, _method in inspect.getmembers(self.definition, predicate=inspect.ismethod):  # type: str, types.MethodType
            if _method_name.startswith("step"):
                # According to https://stackoverflow.com/questions/41900639/python-unable-to-compare-bound-method-to-itself#41900748,
                # we shall use `==` and not `is` for the test below.
                if _method == self.definition.section:  # type: ignore[comparison-overlap]  ## left: "UnboundMethodType", right: "Callable[[str], StepSection]"
                    self._logger.debug("Skipping %r", _method)
                    continue
                self._logger.debug("  Method: %s()", _method_name)
                _methods.append(_method)

        # Sort methods.
        StepMethods.sortbynames(self._logger, _methods)

        # Eventually build the `StepDefinition` objects.
        for _method in _methods:  # `_method` already defined.
            self.definition.addstep(StepDefinition(method=_method))
