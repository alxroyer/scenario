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
    from ._logger import Logger as _LoggerType
    from ._loggermain import MainLogger as _MainLoggerType
    from ._req import Req as _ReqType
    from ._reqdb import ReqDatabase as _ReqDatabaseType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._reqverifier import ReqVerifierHelper as _ReqVerifierHelperType
    from ._scenarioconfig import ScenarioConfig as _ScenarioConfigType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._scenariostack import ScenarioStack as _ScenarioStackType
    from ._stepdefinition import StepDefinition as _StepDefinitionType


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

    # Optimize attribute access for this class.
    __slots__ = [
        "_code_location_cls",
        "_config_db",
        "_execution_locations",
        "_main_logger",
        "_reflection_logger",
        "_req_cls",
        "_req_db",
        "_req_ref_cls",
        "_req_verifier_cls",
        "_req_verifier_helper_cls",
        "_scenario_config",
        "_scenario_definition_cls",
        "_scenario_stack",
        "_step_definition_cls",
        "args",
    ]

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

        #: :class:`._loggermain.MainLogger` singleton reference.
        #:
        #: Reference resolved by :meth:`main_logger()` property.
        self._main_logger = None  # type: typing.Optional[_MainLoggerType]

        #: :class:`._logger.Logger` singleton for reflective programming.
        #:
        #: Instanciated by :meth:`reflection_logger()` property.
        #:
        #: .. note:: Not instanciated in :mod:`._reflection`, but here with this :class:`FastPath` class.
        self._reflection_logger = None  # type: typing.Optional[_LoggerType]

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

        #: :class:`._scenariostack.ScenarioStack` singleton reference.
        #:
        #: Reference resolved by :meth:`scenario_stack()` property.
        self._scenario_stack = None  # type: typing.Optional[_ScenarioStackType]

        #: :class:`._reqdb.ReqDatabase` singleton reference.
        #:
        #: Reference resolved by :meth:`req_db()` property.
        self._req_db = None  # type: typing.Optional[_ReqDatabaseType]

        # Classes.

        #: :class:`._scenariodefinition.ScenarioDefinition` class reference.
        #:
        #: Reference resolved by :meth:`scenario_definition_cls()` property.
        self._scenario_definition_cls = None  # type: typing.Optional[typing.Type[_ScenarioDefinitionType]]

        #: :class:`._stepdefinition.StepDefinition` class reference.
        #:
        #: Reference resolved by :meth:`step_definition_cls()` property.
        self._step_definition_cls = None  # type: typing.Optional[typing.Type[_StepDefinitionType]]

        #: :class:`._req.Req` class reference.
        #:
        #: Reference resolved by :meth:`req_cls()` property.
        self._req_cls = None  # type: typing.Optional[typing.Type[_ReqType]]

        #: :class:`._reqref.ReqRef` class reference.
        #:
        #: Reference resolved by :meth:`req_ref_cls()` property.
        self._req_ref_cls = None  # type: typing.Optional[typing.Type[_ReqRefType]]

        #: :class:`._reqverifier.ReqVerifier` class reference.
        #:
        #: Reference resolved by :meth:`req_verifier_cls()` property.
        self._req_verifier_cls = None  # type: typing.Optional[typing.Type[_ReqVerifierType]]

        #: :class:`._reqverifier.ReqVerifierHelper` class reference.
        #:
        #: Reference resolved by :meth:`req_verifier_helper_cls()` property.
        self._req_verifier_helper_cls = None  # type: typing.Optional[typing.Type[_ReqVerifierHelperType]]

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
    def main_logger(self):  # type: () -> _MainLoggerType
        """
        :class:`._loggermain.MainLogger` singleton.
        """
        if self._main_logger is None:
            from ._loggermain import MAIN_LOGGER  # check-imports: ignore  ## `FastPath` local import.
            self._main_logger = MAIN_LOGGER
        return self._main_logger

    @property
    def reflection_logger(self):  # type: () -> _LoggerType
        """
        :class:`._logger.Logger` singleton for reflective programming.
        """
        if self._reflection_logger is None:
            from ._debugclasses import DebugClass  # check-imports: ignore  ## `FastPath` local import.
            from ._logger import Logger  # check-imports: ignore  ## `FastPath` local import.

            self._reflection_logger = Logger(log_class=DebugClass.REFLECTION)
        return self._reflection_logger

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
    def scenario_stack(self):  # type: () -> _ScenarioStackType
        """
        :class:`._scenariostack.ScenarioStack` singleton.
        """
        if self._scenario_stack is None:
            from ._scenariostack import SCENARIO_STACK  # check-imports: ignore  ## `FastPath` local import.
            self._scenario_stack = SCENARIO_STACK
        return self._scenario_stack

    @property
    def req_db(self):  # type: () -> _ReqDatabaseType
        """
        :class:`._reqdb.ReqDatabase` singleton.
        """
        if self._req_db is None:
            from ._reqdb import REQ_DB  # check-imports: ignore  ## `FastPath` local import.
            self._req_db = REQ_DB
        return self._req_db

    @property
    def scenario_definition_cls(self):  # type: () -> typing.Type[_ScenarioDefinitionType]
        """
        :class:`._scenariodefinition.ScenarioDefinition` class reference.
        """
        if self._scenario_definition_cls is None:
            from ._scenariodefinition import ScenarioDefinition  # check-imports: ignore  ## `FastPath` local import.
            self._scenario_definition_cls = ScenarioDefinition
        return self._scenario_definition_cls

    @property
    def step_definition_cls(self):  # type: () -> typing.Type[_StepDefinitionType]
        """
        :class:`._stepdefinition.StepDefinition` class reference.
        """
        if self._step_definition_cls is None:
            from ._stepdefinition import StepDefinition  # check-imports: ignore  ## `FastPath` local import.
            self._step_definition_cls = StepDefinition
        return self._step_definition_cls

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

    @property
    def req_verifier_cls(self):  # type: () -> typing.Type[_ReqVerifierType]
        """
        #: :class:`._reqverifier.ReqVerifier` class reference.
        """
        if self._req_verifier_cls is None:
            from ._reqverifier import ReqVerifier  # check-imports: ignore  ## `FastPath` local import.
            self._req_verifier_cls = ReqVerifier
        return self._req_verifier_cls

    @property
    def req_verifier_helper_cls(self):  # type: () -> typing.Type[_ReqVerifierHelperType]
        """
        #: :class:`._reqverifier.ReqVerifierHelper` class reference.
        """
        if self._req_verifier_helper_cls is None:
            from ._reqverifier import ReqVerifierHelper  # check-imports: ignore  ## `FastPath` local import.
            self._req_verifier_helper_cls = ReqVerifierHelper
        return self._req_verifier_helper_cls


#: Main instance of :class:`FastPath`.
FAST_PATH = FastPath()
