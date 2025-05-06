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

import traceback
import types
import typing

if True:
    from ._assertions import Assertions as _AssertionsImpl  # @inheritance
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
    from ._locations import CodeLocation as _CodeLocationImpl  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
    from ._reqverifier import ReqVerifier as _ReqVerifierImpl  # @inheritance
    from ._stepuserapi import StepUserApi as _StepUserApiImpl  # @inheritance
if typing.TYPE_CHECKING:
    from ._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from ._knownissues import KnownIssue as _KnownIssueType
    from ._locations import CodeLocation as _CodeLocationType
    from ._reflection import Reflection as _ReflectionType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._stepexecution import StepExecution as _StepExecutionType
    from ._stepspecifications import AnyStepDefinitionSpecificationType as _AnyStepDefinitionSpecificationType


class StepDefinition(_StepUserApiImpl, _AssertionsImpl, _LoggerImpl, _ReqVerifierImpl):
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
        def _ensurereturntype(step_definition):  # type: (StepDefinition) -> VarStepDefinitionType
            """
            Avoids using ``# type: ignore`` pragmas every time this :meth:`StepDefinition.getinstance()` method returns a value.
            """
            _step_definition = typing.cast(typing.Any, step_definition)  # type: VarStepDefinitionType  # noqa  ## Shadows name '_step_definition' from outer scope
            return _step_definition

        _step_specification = cls if (index is None) else (cls, index)  # type: _AnyStepDefinitionSpecificationType
        if _FAST_PATH.scenario_stack.building.scenario_definition:
            _step_definition = _FAST_PATH.scenario_stack.building.scenario_definition.getstep(_step_specification)  # type: typing.Optional[StepDefinition]
            if _step_definition is not None:
                return _ensurereturntype(_step_definition)
        if _FAST_PATH.scenario_stack.current_scenario_definition:
            _step_definition = _FAST_PATH.scenario_stack.current_scenario_definition.getstep(_step_specification)  # Type already defined above.
            if _step_definition is not None:
                return _ensurereturntype(_step_definition)
        if not (_FAST_PATH.scenario_stack.building.scenario_definition or _FAST_PATH.scenario_stack.current_scenario_definition):
            _FAST_PATH.scenario_stack.raisecontexterror("No current scenario definition")
        else:
            _FAST_PATH.scenario_stack.raisecontexterror(f"No such step definition of type {_FAST_PATH.reflection.qualname(cls)}")

    def __init__(
            self,
            method=None,  # type: typing.Optional[types.MethodType]
            numbered=True,  # type: bool
    ):  # type: (...) -> None
        """
        :param method: Method that defines the step, when applicable. Optional.
        :param numbered: ``False`` if the step shall not be numbered.
        """
        #: Step name cache.
        #:
        #: Computed on demand and cached by the :meth:`name()` property.
        self.__name_cache = None  # type: typing.Optional[str]

        #: Owner scenario.
        #:
        #: Set when :meth:`._scenariodefinition.ScenarioDefinition.addstep()` is called.
        self._scenario = None  # type: typing.Optional[_ScenarioDefinitionType]

        #: Step method, if any.
        self.method = method  # type: typing.Optional[types.MethodType]

        #: Definition location cache.
        #:
        #: Computed on demand and cached by the :meth:`location()` property.
        #: May be explicitly set by the :meth:`location()` setter.
        self.__location_cache = None  # type: typing.Optional[_CodeLocationType]

        #: Instantiation call stack (when applicable).
        self.__instantiation_stack = ()  # type: typing.Sequence[traceback.FrameSummary]
        if StepDefinitionHelper(self).issubclass():
            self.__instantiation_stack = traceback.extract_stack()

        #: ``True`` when the step may be assigned a step :attr:`number`.
        #:
        #: When ``False``, :meth:`number()` consequently returns 0.
        self.numbered = numbered

        _StepUserApiImpl.__init__(self)
        _AssertionsImpl.__init__(self)
        _LoggerImpl.__init__(self, log_class=self.name)
        _ReqVerifierImpl.__init__(self)

        # Activate debugging by default for step definitions.
        self.enabledebug(True)

        #: Step description.
        self.description = None  # type: typing.Optional[str]
        #: List of actions and expected results that define the step.
        self.__action_result_definitions = []  # type: typing.List[_ActionResultDefinitionType]

        #: Step executions.
        self.executions = []  # type: typing.List[_StepExecutionType]

    def __repr__(self):  # type: () -> str
        """
        Canonical string representation.
        """
        if type(self) is StepDefinition:
            return f"<{_FAST_PATH.reflection.qualname(type(self))} {self.name!r}>"
        else:
            return f"<{_FAST_PATH.reflection.qualname(type(self))}#{self.number}>"

    def __str__(self):  # type: () -> str
        """
        Returns a human readable representation of the step definition.
        """
        return f"step#{self.number} ({self.name})"

    @property
    def name(self):  # type: () -> str
        """
        Step name, i.e. the qualified name of the class or method defining it.
        """
        if self.__name_cache is None:
            if self.method:
                self.__name_cache = _FAST_PATH.reflection.qualname(self.method)
            else:
                self.__name_cache = _FAST_PATH.reflection.qualname(type(self))
        return self.__name_cache

    @property
    def location(self):  # type: () -> _CodeLocationType
        """
        Definition location getter.
        """
        # First try to resolve the step location as its instantiation location in the owner scenario initializer.
        if (self.__location_cache is None) and StepDefinitionHelper(self).issubclass():
            # Walk backward the instantiation stack caught in `__init__()`,
            # skip `StepDefinition` (or subclass) initializer locations,
            # and search for a consecutive `ScenarioDefinition` (or subclass) initializer location.
            for _tb_item in reversed(self.__instantiation_stack):  # type: traceback.FrameSummary
                # Retrieve code owners for the current traceback item.
                _code_owners = _FAST_PATH.reflection.codeowners(
                    file=_tb_item.filename,
                    line=_tb_item.lineno or -1,
                    name=_tb_item.name,
                )  # type: typing.Optional[typing.Sequence[_ReflectionType.CodeOwnerType]]

                # Check the `codeowners()` call succeeded
                # and returned a sequence ending with [..., class, method] items
                # (no need to check that the last item is a method).
                if (
                    _code_owners
                    and (len(_code_owners) >= 2) and isinstance(_code_owners[-2], type)
                ):
                    _cls = _code_owners[-2]  # type: type

                    # Skip `StepDefinition` (or subclass) initializers.
                    if issubclass(_cls, _FAST_PATH.step_definition_cls) and (_tb_item.name == "__init__"):
                        continue

                    # Expect the consecutive location is a `ScenarioDefinition` (or subclass) initializer.
                    if issubclass(_cls, _FAST_PATH.scenario_definition_cls) and (_tb_item.name == "__init__"):
                        self.__location_cache = _CodeLocationImpl.fromtbitem(_tb_item)
                        # If found as expected, stop walking the instantiation stack.
                        break

                # Unexpected situations => abort with debug info.
                self.debug("%r => _code_owners=%r => break instantiation location resolution for %r", _tb_item, _code_owners, self.name)
                break

        # Default to regular resolution: from the method or class defining the step.
        if self.__location_cache is None:
            if self.method:
                self.__location_cache = _CodeLocationImpl.fromcodeowner(self.method)
            else:
                self.__location_cache = _CodeLocationImpl.fromcodeowner(type(self))

        return self.__location_cache

    @location.setter
    def location(self, location):  # type: (_CodeLocationType) -> None
        """
        Definition location setter.
        """
        self.__location_cache = location

    def displaynameandlocation(self):  # type: (...) -> str
        """
        Computes a display string for the step name and location.

        :return: Display string for the step name and location.
        """
        if StepDefinitionHelper(self).isinstantiationlocation():
            return f"{self.location.file}:{self.location.line} - {self.name}"
        else:
            return f"{self.location.tolongstring()}"

    @property
    def scenario(self):  # type: () -> _ScenarioDefinitionType
        """
        Owner scenario.
        """
        if self._scenario is None:
            raise RuntimeError(f"Owner scenario not set yet for {self!r}")
        return self._scenario

    @scenario.setter
    def scenario(self, scenario):  # type: (_ScenarioDefinitionType) -> None
        """
        Owner scenario setter.
        """
        if self._scenario is not None:
            raise RuntimeError(f"Owner scenario already set for {self!r} with {self._scenario!r}, can't set {scenario!r}")
        self._scenario = scenario

    @property
    def number(self):  # type: () -> int
        """
        Step definition number.

        Number of this step definition within the steps defining the related scenario.
        Starting from 1, as displayed to the user.
        """
        if not self.numbered:
            return 0

        _step_number = 0  # type: int
        for _step_definition in self.scenario.steps:  # type: StepDefinition
            # Count numbered steps only.
            if _step_definition.numbered:
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
        assert self.method is not None, f"{self} not implemented"
        _FAST_PATH.scenario_runner.debug("Invoking %r", self.method)
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
        Instantiates a helper for the given step definition.

        :param definition: Step definition instance this helper works for.
        """
        #: Step definition instance this helper works for.
        self.definition = definition

    def issubclass(self):  # type: (...) -> bool
        """
        Determines whether the related step definition is defined by a subclass of :class:`StepDefinition`.
        """
        return (
            (self.definition.method is None)
            and (type(self.definition) is not StepDefinition)
        )

    def isinstantiationlocation(self):  # type: (...) -> bool
        """
        Determines whether the location of the related step is an instantiation location.
        """
        return (
            # The step should be an instance of a `StepDefinition` subclass.
            self.issubclass()
            # The code owner of the location should match with the scenario definition class of the owner scenario.
            and isinstance(self.definition.location.code_owner, type)
            and isinstance(self.definition.scenario, self.definition.location.code_owner)
        )

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
