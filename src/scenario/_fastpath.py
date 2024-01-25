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
No-dependency module that makes data available without importing other modules.

Avoids cyclic module dependencies, and numerous local imports in the same time.

Nevertheless, usage of this global data approach shall be reserved when performance issues are revealed,
and justified in the related data docstring.
"""

import typing

if typing.TYPE_CHECKING:
    from ._args import Args as _ArgsType
    from ._configdb import ConfigDatabase as _ConfigDatabaseType
    from ._locations import CodeLocation as _CodeLocationType
    from ._locations import ExecutionLocations as _ExecutionLocationsType
    from ._req import Req as _ReqType
    from ._reqref import ReqRef as _ReqRefType
    from ._scenarioconfig import ScenarioConfig as _ScenarioConfigType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class FastPath:
    """
    Fast path data container.

    Avoids numerous local imports, especially in low-level functions (like logging functions for instance).

    .. note::
        Class references provided through :class:`FastPath` attributes so that they can be accessed
        without making a local import,
        and without creating a cyclic module dependency.

        To be used with parcimony.
        Prefer importing the class at the module level with implementation imports
        when there is no risk about potential future cyclic module dependencies.
    """

    def __init__(self):  # type: (...) -> None
        """
        Declares fast path data.
        """
        # Instances.

        #: :class:`._locations.CodeLocation` class reference.
        #:
        #: Reference resolved by :meth:`code_location()` property.
        self._code_location_cls = None  # type: typing.Optional[typing.Type[_CodeLocationType]]

        #: :class:`._locations.ExecutionLocations` singleton reference.
        #:
        #: Reference resolved by :meth:`execution_locations()` property.
        self._execution_locations = None  # type: typing.Optional[_ExecutionLocationsType]

        #: :class:`._args.Args` instance installed.
        #:
        #: Reference set by :meth:`._args.Args.setinstance()`.
        self.args = None  # type: typing.Optional[_ArgsType]

        #: :class:`._configdb.ConfigDatabase` singleton reference.
        #:
        #: Reference resolved by :meth:`config_db()` property.
        self._config_db = None  # type: typing.Optional[_ConfigDatabaseType]

        #: :class:`._scenarioconfig.ScenarioConfig` singleton reference.
        #:
        #: Reference resolved by :meth:`scenario_config()` property.
        self._scenario_config = None  # type: typing.Optional[_ScenarioConfigType]

        # Classes.

        #: :class:`._scenariodefinition.ScenarioDefinition` class reference.
        #:
        #: Reference resolved by :meth:`scenario_definition_cls()` property.
        self._scenario_definition_cls = None  # type: typing.Optional[typing.Type[_ScenarioDefinitionType]]

        #: :class:`._req.Req` class reference.
        #:
        #: Reference resolved by :meth:`req_cls()` property.
        self._req_cls = None  # type: typing.Optional[typing.Type[_ReqType]]

        #: :class:`._reqref.ReqRef` class reference.
        #:
        #: Reference resolved by :meth:`req_ref_cls()` property.
        self._req_ref_cls = None  # type: typing.Optional[typing.Type[_ReqRefType]]

    @property
    def code_location(self):  # type: () -> typing.Type[_CodeLocationType]
        """
        Container for :class:`._locations.CodeLocation` static methods.
        """
        if self._code_location_cls is None:
            from ._locations import CodeLocation  # check-imports: ignore  ## `FastPath` local import.
            self._code_location_cls = CodeLocation
        return self._code_location_cls

    @property
    def execution_locations(self):  # type: () -> _ExecutionLocationsType
        """
        :class:`._locations.ExecutionLocations` singleton.
        """
        if self._execution_locations is None:
            from ._locations import EXECUTION_LOCATIONS  # check-imports: ignore  ## `FastPath` local import.
            self._execution_locations = EXECUTION_LOCATIONS
        return self._execution_locations

    @property
    def config_db(self):  # type: () -> _ConfigDatabaseType
        """
        :class:`._configdb.ConfigDatabase` singleton.
        """
        if self._config_db is None:
            from ._configdb import CONFIG_DB  # check-imports: ignore  ## `FastPath` local import.
            self._config_db = CONFIG_DB
        return self._config_db

    @property
    def scenario_config(self):  # type: () -> _ScenarioConfigType
        """
        :class:`._scenarioconfig.ScenarioConfig` singleton.
        """
        if self._scenario_config is None:
            from ._scenarioconfig import SCENARIO_CONFIG  # check-imports: ignore  ## `FastPath` local import.
            self._scenario_config = SCENARIO_CONFIG
        return self._scenario_config

    @property
    def scenario_definition_cls(self):  # type: () -> typing.Type[_ScenarioDefinitionType]
        """
        #: :class:`._scenariodefinition.ScenarioDefinition` class reference.
        """
        if self._scenario_definition_cls is None:
            from ._scenariodefinition import ScenarioDefinition  # check-imports: ignore  ## `FastPath` local import.
            self._scenario_definition_cls = ScenarioDefinition
        return self._scenario_definition_cls

    @property
    def req_cls(self):  # type: () -> typing.Type[_ReqType]
        """
        #: :class:`._req.Req` class reference.
        """
        if self._req_cls is None:
            from ._req import Req  # check-imports: ignore  ## `FastPath` local import.
            self._req_cls = Req
        return self._req_cls

    @property
    def req_ref_cls(self):  # type: () -> typing.Type[_ReqRefType]
        """
        #: :class:`._reqref.ReqRef` class reference.
        """
        if self._req_ref_cls is None:
            from ._reqref import ReqRef  # check-imports: ignore  ## `FastPath` local import.
            self._req_ref_cls = ReqRef
        return self._req_ref_cls


#: Main instance of :class:`FastPath`.
FAST_PATH = FastPath()
