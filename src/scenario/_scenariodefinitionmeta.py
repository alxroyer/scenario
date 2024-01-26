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
Metaclass for :class:`._scenariodefinition.ScenarioDefinition`.

Ensures functioning with :class:`._scenariostack.ScenarioStack` on :class:`._scenariodefinition.ScenarioDefinition` instanciations.
"""

import abc
import types
import typing

if True:
    from ._fastpath import FAST_PATH as _FAST_PATH  # `FAST_PATH` imported once for performance concerns.
if typing.TYPE_CHECKING:
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class MetaScenarioDefinition(abc.ABCMeta):
    """
    Metaclass for :class:`._scenariodefinition.ScenarioDefinition`.

    .. note::
        So that it can be a metaclass for :class:`._scenariodefinition.ScenarioDefinition`,
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
        Overloads class definition of :class:`._scenariodefinition.ScenarioDefinition` class and subclasses.

        Sets :class:`MetaScenarioDefinition.InitWrapper` instances in place of ``__init__()`` methods,
        in order to have :class:`._scenariodefinition.ScenarioDefinition` initializers enclosed with
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
        Wrapper for ``__init__()`` methods of :class:`._scenariodefinition.ScenarioDefinition` instances.

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
            # Note:
            #   `mypy` (as of 0.910 to 1.0.1) seems to mess up between `types.FunctionType` and `types.MethodType`
            #   when assigning the `init_method` member variable below.
            #   Let's use `typing.cast(Any)` to work around it.

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

                First item should normally be the :class:`._scenariodefinition.ScenarioDefinition` instance the initializer is executed for.
            :param kwargs:
                Named arguments.

            Pushes the scenario definition to the building context of the scenario stack before the initializer's execution,
            then removes it out after the initializer's execution.
            """
            from ._scenariostack import SCENARIO_STACK

            _scenario_definition = None  # type: typing.Optional[_ScenarioDefinitionType]
            if (len(args) >= 1) and isinstance(args[0], _FAST_PATH.scenario_definition_cls):
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
