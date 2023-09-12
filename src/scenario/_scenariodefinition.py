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

if True:
    from ._assertions import Assertions as _AssertionsImpl  # `Assertions` used for inheritance.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._reqtracker import ReqTracker as _ReqTrackerImpl  # `ReqTracker` used for inheritance.
    from ._stepuserapi import StepUserApi as _StepUserApiImpl  # `StepUserApi` used for inheritance.
if typing.TYPE_CHECKING:
    from ._path import AnyPathType as _AnyPathType
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._setutils import OrderedSetType as _OrderedSetType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._stepdefinition import VarStepDefinitionType as _VarStepDefinitionType
    from ._stepsection import StepSectionDescription as _StepSectionDescriptionType
    from ._stepspecifications import AnyStepDefinitionSpecificationType as _AnyStepDefinitionSpecificationType


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


class ScenarioDefinition(_StepUserApiImpl, _AssertionsImpl, _LoggerImpl, _ReqTrackerImpl, metaclass=MetaScenarioDefinition):
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
        from ._reflection import qualname
        from ._scenariostack import SCENARIO_STACK

        if isinstance(SCENARIO_STACK.building.scenario_definition, cls):
            return SCENARIO_STACK.building.scenario_definition
        if isinstance(SCENARIO_STACK.current_scenario_definition, cls):
            return SCENARIO_STACK.current_scenario_definition
        SCENARIO_STACK.raisecontexterror(f"Current scenario definition not of type {qualname(cls)}")

    def __init__(
            self,
            title=None,  # type: typing.Optional[str]
            description=None,  # type: typing.Optional[str]
    ):  # type: (...) -> None
        """
        Initializes a scenario instance with optional title and description.

        :param title: Short scenario title.
        :param description: Longer scenario description.

        Determines the scenario name and *log class* by the way from the scenario script path.

        Activates debugging by default.
        """
        from ._locations import CodeLocation
        from ._path import Path
        from ._scenarioexecution import ScenarioExecution

        #: Scenario title, optional.
        #:
        #: As short as possible.
        #: Usually a couple of words, in the nominal form.
        self.title = title or ""  # type: str

        #: Scenario description, optional.
        #:
        #: More detailed explanation about the scenario than :attr:`title`.
        #: Commonly describes the purpose or objectives of the test.
        self.description = description or ""  # type: str

        #: Definition location.
        self.location = CodeLocation.fromclass(type(self))  # type: CodeLocation

        #: Script path.
        self.script_path = Path(self.location.file)  # type: Path

        #: Scenario name: i.e. script pretty path.
        self.name = self.script_path.prettypath  # type: str

        _StepUserApiImpl.__init__(self)
        _AssertionsImpl.__init__(self)
        _LoggerImpl.__init__(self, log_class=self.name)
        _ReqTrackerImpl.__init__(self)

        # Activate debugging by default for scenario definitions.
        self.enabledebug(True)

        #: Continue on error option.
        #:
        #: Local configuration for the current scenario.
        #: Prevails on :meth:`._scenarioconfig.ScenarioConfig.continueonerror()`.
        #:
        #: Not set by default.
        self.__continue_on_error = None  # type: typing.Optional[bool]

        #: User scenario attributes (see :meth:`._scenarioconfig.ScenarioConfig.expectedscenarioattributes()`).
        #:
        #: .. seealso:: :class:`._scenarioattributes.CoreScenarioAttributes` for core scenario attributes.
        self.__user_attributes = {}  # type: typing.Dict[str, typing.Any]

        #: Check step requirement coverage option.
        self.__check_step_req_coverage = None  # type: typing.Optional[bool]

        #: List of steps that define the scenario.
        self.__step_definitions = []  # type: typing.List[_StepDefinitionType]

        #: Scenario execution, if any.
        self.execution = None  # type: typing.Optional[ScenarioExecution]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation of the scenario definition.
        """
        from ._reflection import qualname

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
        Defines a user attribute, or sets a core attribute, for the scenario.

        :param name: Attribute name.
        :param value: Attribute value.
        :return: ``self``
        """
        from ._enumutils import enum2str
        from ._scenarioattributes import CoreScenarioAttributes

        # Core scenario attributes.
        if name == CoreScenarioAttributes.TITLE:
            if not isinstance(value, str):
                raise ValueError(f"Invalid scenario title {value!r}")
            self.title = value
            return self
        if name == CoreScenarioAttributes.DESCRIPTION:
            if not isinstance(value, str):
                raise ValueError(f"Invalid scenario description {value!r}")
            self.description = value
            return self
        if name in CoreScenarioAttributes:
            raise NotImplementedError(f"Core scenario attribute {name!r} not handled")

        # User scenario attributes.
        self.__user_attributes[enum2str(name)] = value
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
        from ._scenarioattributes import CoreScenarioAttributes

        # Core scenario attributes.
        if name == CoreScenarioAttributes.TITLE:
            return self.title
        if name == CoreScenarioAttributes.DESCRIPTION:
            return self.description
        if name in CoreScenarioAttributes:
            raise NotImplementedError(f"Core scenario attribute {name!r} not handled")

        # User scenario attributes.
        return self.__user_attributes[enum2str(name)]

    def getattributenames(self):  # type: (...) -> typing.Sequence[str]
        """
        Retrieves all attribute names defined with the scenario.

        :return: List of attribute names.
        """
        from ._scenarioattributes import CoreScenarioAttributes

        return [
            # Core scenario attributes first.
            *[str(_core_scenario_attribute) for _core_scenario_attribute in CoreScenarioAttributes],
            # User scenario attributes after.
            *[_name for _name in self.__user_attributes],
        ]

    def getreqs(
            self,
            *,
            walk_steps=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqType]
        """
        :meth:`._reqtracker.ReqTracker.getreqrefs()` override for the ``walk_steps`` option augmentation.

        :param walk_steps:
            Option to include step requirements.

            If ``True``, requirements tracked by the scenario steps will be included in the result.

            ``False`` by default.
        :return:
            Same as :meth:`._reqtracker.ReqTracker.getreqs()`.
        """
        from ._setutils import OrderedSetHelper

        return OrderedSetHelper.build(
            # Convert link >> requirement.
            map(
                lambda p_req_link: p_req_link.req_ref.req,
                self.getreqlinks(walk_steps=walk_steps),
            ),
            # Sort by requirement ids.
            key=lambda req: req.id,
        )

    def getreqrefs(
            self,
            *,
            walk_steps=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqRefType]
        """
        :meth:`._reqtracker.ReqTracker.getreqrefs()` override for the ``walk_steps`` option augmentation.

        :param walk_steps:
            Option to include step requirement references.

            If ``True``, requirement references tracked by the scenario steps will be included in the result.

            ``False`` by default.
        :return:
            Same as :meth:`._reqtracker.ReqTracker.getreqrefs()`.
        """
        from ._setutils import OrderedSetHelper

        return OrderedSetHelper.build(
            # Convert link >> requirement reference.
            map(
                lambda p_req_link: p_req_link.req_ref,
                self.getreqlinks(walk_steps=walk_steps),
            ),
            # Sort by requirement reference ids.
            key=lambda req_ref: req_ref.id,
        )

    def getreqlinks(
            self,
            req_ref=None,  # type: _AnyReqRefType
            *,
            walk_steps=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        :meth:`._reqtracker.ReqTracker.getreqlinks()` override for the ``walk_steps`` option augmentation.

        :param req_ref:
            Same as :meth:`._reqtracker.ReqTracker.getreqlinks()`.
        :param walk_steps:
            Option to include step requirement links.

            If ``True``, links held by the scenario steps will be included in the result.

            ``False`` by default.

            .. tip::
                Retrieving the direct requirement links from the current tracker
                can also be done through the :attr:`._reqtracker.ReqTracker.req_links` attribute.
        :return:
            Same as :meth:`._reqtracker.ReqTracker.getreqlinks()`.
        """
        from ._reqlink import ReqLinkHelper
        from ._setutils import OrderedSetHelper

        # Constitute the whole list of requirement links to consider, depending on the `walk_steps` option.
        _req_links = list(self._req_links)  # type: typing.List[_ReqLinkType]
        if walk_steps:
            for _step in self.steps:  # type: _StepDefinitionType
                _req_links.extend(_step._req_links)

        return OrderedSetHelper.build(
            # Filter this list with the requirement predicates.
            filter(
                lambda req_link: req_link.matches(req_ref=req_ref),
                _req_links,
            ),
            # Sort by requirement reference ids.
            key=ReqLinkHelper.key,
        )

    def checkstepreqcoverage(
            self,  # type: VarScenarioDefinitionType
            check_step_req_coverage,  # type: typing.Optional[bool]
    ):  # type: (...) -> VarScenarioDefinitionType
        """
        Sets the local configuration for this scenario be supposed to refine its requirement coverage on steps.

        .. note:: Overrides the :meth:`._scenarioconfig.ScenarioConfig.checkstepreqcoverage()` global configuration.

        :param check_step_req_coverage:
            New `check step requirement coverage` local configuration.

            ``None`` to rely on the :meth:`._scenarioconfig.ScenarioConfig.checkstepreqcoverage()` global configuration again.
        :return:
            ``self``
        """
        self.__check_step_req_coverage = check_step_req_coverage
        return self

    @property
    def check_step_req_coverage(self):  # type: () -> bool
        """
        Tells whether the requirements tracked by this scenario should be refined on steps.

        Takes the local configuration at first,
        then the :meth:`._scenarioconfig.ScenarioConfig.checkstepreqcoverage()` global configuration.
        """
        from ._scenarioconfig import SCENARIO_CONFIG

        if self.__check_step_req_coverage is not None:
            return self.__check_step_req_coverage
        else:
            return SCENARIO_CONFIG.checkstepreqcoverage()

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
            step_definition,  # type: _VarStepDefinitionType
    ):  # type: (...) -> _VarStepDefinitionType
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
            step_specification,  # type: _AnyStepDefinitionSpecificationType
    ):  # type: (...) -> typing.Optional[_StepDefinitionType]
        """
        Finds a step definition.

        :param step_specification: Step specification (see :obj:`._stepspecifications.AnyStepDefinitionSpecificationType`).
        :return: Step definition found, if any. ``None`` otherwise.
        """
        from ._stepspecifications import StepDefinitionSpecification

        if not isinstance(step_specification, StepDefinitionSpecification):
            step_specification = StepDefinitionSpecification(step_specification)
        return step_specification.resolve()

    def expectstep(
            self,
            step_specification,  # type: _AnyStepDefinitionSpecificationType
    ):  # type: (...) -> _StepDefinitionType
        """
        Expects a step definition.

        When the step cannot be found, an exception is raised.

        :param step_specification: Step specification (see :obj:`._stepspecifications.AnyStepDefinitionSpecificationType`).
        :return: Expected step definition.
        :raise LookupError: When the step definition could not be found.
        """
        from ._stepspecifications import StepDefinitionSpecification

        if not isinstance(step_specification, StepDefinitionSpecification):
            step_specification = StepDefinitionSpecification(step_specification)
        return step_specification.expect()

    @property
    def steps(self):  # type: () -> typing.List[_StepDefinitionType]
        """
        Step list.
        """
        return self.__step_definitions.copy()

    def continueonerror(
            self,  # type: VarScenarioDefinitionType
            continue_on_error,  # type: typing.Optional[bool]
    ):  # type: (...) -> VarScenarioDefinitionType
        """
        Sets the local configuration for this scenario to continue on error or not.

        .. note:: Overrides the :meth:`._scenarioconfig.ScenarioConfig.continueonerror()` global configuration.

        :param continue_on_error:
            *Continue on error* local configuration.

            ``None`` to unset and rely on the :meth:`._scenarioconfig.ScenarioConfig.continueonerror()` global configuration again.
        :return:
            ``self``
        """
        self.__continue_on_error = continue_on_error
        return self

    @property
    def continue_on_error(self):  # type: () -> bool
        """
        Tells whether this scenario shall continue on error or not.

        Takes the local configuration at first,
        then the :meth:`._scenarioconfig.ScenarioConfig.continueonerror()` global configuration.
        """
        from ._scenarioconfig import SCENARIO_CONFIG

        if self.__continue_on_error is not None:
            return self.__continue_on_error
        else:
            return SCENARIO_CONFIG.continueonerror()

    @continue_on_error.setter
    def continue_on_error(self, continue_on_error):  # type: (typing.Optional[bool]) -> None
        """
        Deprecated. Please use :meth:`continueonerror()` instead.

        .. warning:: Deprecated.
        """
        self.warning(f"Setting the `ScenarioDefintion.continue_on_error` attribute is now deprecated. Please use the `continueonerror()` method instead.")
        self.continueonerror(continue_on_error)


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
            script_path,  # type: _AnyPathType
    ):  # type: (...) -> typing.Type[ScenarioDefinition]
        """
        Retrieves the scenario definitions classes from a Python script.

        :param script_path: Path of a Python script.
        :return: Scenario definition classes, if any.
        """
        from ._path import Path
        from ._reflection import importmodulefrompath

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
        from ._logger import Logger
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
        from ._reflection import qualname
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
