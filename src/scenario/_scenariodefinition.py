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

import enum
import inspect
import types
import typing

if True:
    from ._assertions import Assertions as _AssertionsImpl  # `Assertions` used for inheritance.
    from ._enumutils import enum2str as _enum2str  # `enum2str()` imported once for performance concerns.
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
    from ._path import Path as _PathImpl  # `Path` imported once for performance concerns.
    from ._reqverifier import ReqVerifier as _ReqVerifierImpl  # `ReqVerifier` used for inheritance.
    from ._scenariodefinitionmeta import MetaScenarioDefinition as _MetaScenarioDefinitionImpl  # `MetaScenarioDefinition` used as metaclass.
    from ._stepuserapi import StepUserApi as _StepUserApiImpl  # `StepUserApi` used for inheritance.
if typing.TYPE_CHECKING:
    from ._locations import CodeLocation as _CodeLocationType
    from ._logger import Logger as _LoggerType
    from ._path import AnyPathType as _AnyPathType
    from ._path import Path as _PathType
    from ._req import Req as _ReqType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqtypes import AnyReqRefType as _AnyReqRefType
    from ._reqtypes import SetWithReqLinksType as _SetWithReqLinksType
    from ._setutils import OrderedSetType as _OrderedSetType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._stepdefinition import VarStepDefinitionType as _VarStepDefinitionType
    from ._stepsection import StepSectionDescription as _StepSectionDescriptionType
    from ._stepspecifications import AnyStepDefinitionSpecificationType as _AnyStepDefinitionSpecificationType
    from ._textutils import AnyLongTextType as _AnyLongTextType


class ScenarioDefinition(_StepUserApiImpl, _AssertionsImpl, _LoggerImpl, _ReqVerifierImpl, metaclass=_MetaScenarioDefinitionImpl):
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

        if isinstance(_FAST_PATH.scenario_stack.building.scenario_definition, cls):
            return _FAST_PATH.scenario_stack.building.scenario_definition
        if isinstance(_FAST_PATH.scenario_stack.current_scenario_definition, cls):
            return _FAST_PATH.scenario_stack.current_scenario_definition
        _FAST_PATH.scenario_stack.raisecontexterror(f"Current scenario definition not of type {qualname(cls)}")

    def __init__(
            self,
            title=None,  # type: typing.Optional[str]
            description=None,  # type: typing.Optional[_AnyLongTextType]
    ):  # type: (...) -> None
        """
        Initializes a scenario instance with optional title and description.

        :param title: Short scenario title.
        :param description: Longer scenario description.

        Determines the scenario name and *log class* by the way from the scenario script path.

        Activates debugging by default.
        """
        from ._scenarioexecution import ScenarioExecution
        from ._textutils import anylongtext2str

        #: Scenario title, optional.
        #:
        #: As short as possible.
        #: Usually a couple of words, in the nominal form.
        self.title = title or ""  # type: str

        #: Scenario description, optional.
        #:
        #: More detailed explanation about the scenario than :attr:`title`.
        #: Commonly describes the purpose or objectives of the test.
        self.description = anylongtext2str(description or "")  # type: str

        #: Definition location.
        self.location = _FAST_PATH.code_location.fromclass(type(self))  # type: _CodeLocationType

        #: Script path.
        self.script_path = _PathImpl(self.location.file)  # type: _PathType

        #: Scenario name: i.e. script pretty path.
        self.name = self.script_path.prettypath  # type: str

        _StepUserApiImpl.__init__(self)
        _AssertionsImpl.__init__(self)
        _LoggerImpl.__init__(self, log_class=self.name)
        _ReqVerifierImpl.__init__(self)

        # Depending on `SCENARIO_CONFIG.scenariodebugloggingenabled()`, enable debug logging for scenarios.
        self.enabledebug(_FAST_PATH.scenario_config.scenariodebugloggingenabled())

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

        #: Expect step requirement refinement local configuration.
        self.__expect_step_req_refinement = None  # type: typing.Optional[bool]

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
        self.__user_attributes[_enum2str(name)] = value
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
        from ._scenarioattributes import CoreScenarioAttributes

        # Core scenario attributes.
        if name == CoreScenarioAttributes.TITLE:
            return self.title
        if name == CoreScenarioAttributes.DESCRIPTION:
            return self.description
        if name in CoreScenarioAttributes:
            raise NotImplementedError(f"Core scenario attribute {name!r} not handled")

        # User scenario attributes.
        return self.__user_attributes[_enum2str(name)]

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
    ):  # type: (...) -> _SetWithReqLinksType[_ReqType]
        """
        :meth:`._reqverifier.ReqVerifier.getreqrefs()` override for the ``walk_steps`` option augmentation.

        :param walk_steps:
            Option to include step requirements.

            If ``True``, requirements verified by the scenario steps will be included in the result.

            ``False`` by default.
        :return:
            Same as :meth:`._reqverifier.ReqVerifier.getreqs()`.
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Determine the list of requirement verifiers to walk through, depending on `walk_steps`.
            [self] if not walk_steps else [self, *self.steps],
            # Get the requirement for each link.
            lambda req_link: [req_link.req],
        )

    def getreqrefs(
            self,
            *,
            walk_steps=False,  # type: bool
    ):  # type: (...) -> _SetWithReqLinksType[_ReqRefType]
        """
        :meth:`._reqverifier.ReqVerifier.getreqrefs()` override for the ``walk_steps`` option augmentation.

        :param walk_steps:
            Option to include step requirement references.

            If ``True``, requirement references verified by the scenario steps will be included in the result.

            ``False`` by default.
        :return:
            Same as :meth:`._reqverifier.ReqVerifier.getreqrefs()`.
        """
        from ._reqlink import ReqLinkHelper

        return ReqLinkHelper.buildsetwithreqlinks(
            # Determine the list of requirement verifiers to walk through, depending on `walk_steps`.
            [self] if not walk_steps else [self, *self.steps],
            # Get the requirement reference for each link.
            lambda req_link: [req_link.req_ref],
        )

    def getreqlinks(
            self,
            req_ref=None,  # type: _AnyReqRefType
            *,
            walk_steps=False,  # type: bool
            walk_subrefs=False,  # type: bool
    ):  # type: (...) -> _OrderedSetType[_ReqLinkType]
        """
        :meth:`._reqverifier.ReqVerifier.getreqlinks()` override for the ``walk_steps`` option augmentation.

        :param req_ref:
            Same as :meth:`._reqverifier.ReqVerifier.getreqlinks()`.
        :param walk_steps:
            Option to include step requirement links.

            If ``True``, links held by the scenario steps will be included in the result.

            ``False`` by default.

            .. tip::
                Retrieving the direct requirement links from the current verifier
                can also be done through the :attr:`._reqverifier.ReqVerifier.req_links` attribute.
        :param walk_subrefs:
            When ``req_ref`` is a main requirement,
            ``True`` makes the links match if they trace a subreference of the requirement.

            Ignored when ``req_ref`` is not set.
        :return:
            Same as :meth:`._reqverifier.ReqVerifier.getreqlinks()`.
        """
        from ._reqlink import ReqLink

        # Constitute the whole list of requirement links to consider, depending on the `walk_steps` option.
        _req_links = list(self._req_links)  # type: typing.List[_ReqLinkType]
        if walk_steps:
            for _step in self.steps:  # type: _StepDefinitionType
                _req_links.extend(_step._req_links)

        return ReqLink.orderedset(
            # Filter this list with the requirement predicates.
            filter(
                lambda req_link: req_link.matches(req_ref=req_ref, walk_subrefs=walk_subrefs),
                _req_links,
            ),
        )

    def expectstepreqrefinement(
            self,  # type: VarScenarioDefinitionType
            expect_step_req_refinement,  # type: typing.Optional[bool]
    ):  # type: (...) -> VarScenarioDefinitionType
        """
        Sets the local configuration for this scenario be supposed to refine its requirement coverage on steps.

        .. note:: Overrides the :meth:`._scenarioconfig.ScenarioConfig.expectstepreqrefinement()` global configuration.

        :param expect_step_req_refinement:
            New `expect step requirement refinement` local configuration.

            ``None`` to rely on the :meth:`._scenarioconfig.ScenarioConfig.expectstepreqrefinement()` global configuration again.
        :return:
            ``self``
        """
        self.__expect_step_req_refinement = expect_step_req_refinement
        return self

    @property
    def expect_step_req_refinement(self):  # type: () -> bool
        """
        Tells whether the requirements verified by this scenario should be refined on steps.

        Takes the local configuration set with :meth:`expectstepreqrefinement()` at first,
        then the :meth:`._scenarioconfig.ScenarioConfig.expectstepreqrefinement()` global configuration.
        """
        if self.__expect_step_req_refinement is not None:
            return self.__expect_step_req_refinement
        else:
            return _FAST_PATH.scenario_config.expectstepreqrefinement()

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
        if self.__continue_on_error is not None:
            return self.__continue_on_error
        else:
            return _FAST_PATH.scenario_config.continueonerror()

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
            sys_modules_cache=True,  # type: bool
    ):  # type: (...) -> typing.Type[ScenarioDefinition]
        """
        Retrieves the scenario definitions classes from a Python script.

        :param script_path: Path of a Python script.
        :param sys_modules_cache: See :func:`._reflection.importmodulefrompath()`.
        :return: Scenario definition classes, if any.
        """
        from ._reflection import importmodulefrompath

        # Load the test scenario module.
        script_path = _PathImpl(script_path)
        _module = importmodulefrompath(script_path, sys_modules_cache=sys_modules_cache)  # type: types.ModuleType

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
        self._logger = SCENARIO_RUNNER  # type: _LoggerType

    def buildsteps(self):  # type: (...) -> None
        """
        Reads the scenario step list by inspecting the user scenario class,
        and feeds the scenario definition step list.
        """
        from ._reflection import qualname
        from ._stepmethods import StepMethods

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
            self.definition.addstep(_FAST_PATH.step_definition_cls(method=_method))
