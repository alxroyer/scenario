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
    from ._actionresultdefinition import ActionResultDefinition as _ActionResultDefinitionType
    from ._actionresultexecution import ActionResultExecution as _ActionResultExecutionType
    from ._args import Args as _ArgsType
    from ._campaignargs import CampaignArgs as _CampaignArgsType
    from ._campaignlogging import CampaignLogging as _CampaignLoggingType
    from ._campaignrunner import CampaignRunner as _CampaignRunnerType
    from ._configdb import ConfigDatabase as _ConfigDatabaseType
    from ._handlers import Handlers as _HandlersType
    from ._locations import ExecutionLocations as _ExecutionLocationsType
    from ._logger import Logger as _LoggerType
    from ._loggermain import MainLogger as _MainLoggerType
    from ._req import Req as _ReqType
    from ._reqdb import ReqDatabase as _ReqDatabaseType
    from ._reqlink import ReqLink as _ReqLinkType
    from ._reqlink import ReqLinkHelper as _ReqLinkHelperType
    from ._reqref import ReqRef as _ReqRefType
    from ._reqverifier import ReqVerifier as _ReqVerifierType
    from ._reqverifier import ReqVerifierHelper as _ReqVerifierHelperType
    from ._scenarioargs import CommonExecArgs as _CommonExecArgsType
    from ._scenarioargs import ScenarioArgs as _ScenarioArgsType
    from ._scenarioconfig import ScenarioConfig as _ScenarioConfigType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType
    from ._scenarioexecution import ScenarioExecution as _ScenarioExecutionType
    from ._scenariologging import ScenarioLogging as _ScenarioLoggingType
    from ._scenariorunner import ScenarioRunner as _ScenarioRunnerType
    from ._scenariostack import ScenarioStack as _ScenarioStackType
    from ._stepdefinition import StepDefinition as _StepDefinitionType
    from ._stepexecution import StepExecution as _StepExecutionType
    from ._stepsection import StepSectionBegin as _StepSectionBeginType
    from ._stepsection import StepSectionDescription as _StepSectionDescriptionType
    from ._stepsection import StepSectionEnd as _StepSectionEndType


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
        "_action_result_definition_cls",
        "_action_result_execution_cls",
        "_args",
        "_campaign_args",
        "_campaign_logging",
        "_campaign_runner",
        "_config_db",
        "_exec_args",
        "_execution_locations",
        "_handlers",
        "_main_logger",
        "_reflection_logger",
        "_req_cls",
        "_req_db",
        "_req_link_cls",
        "_req_link_helper_cls",
        "_req_ref_cls",
        "_req_verifier_cls",
        "_req_verifier_helper_cls",
        "_scenario_args",
        "_scenario_config",
        "_scenario_definition_cls",
        "_scenario_execution_cls",
        "_scenario_logging",
        "_scenario_runner",
        "_scenario_stack",
        "_step_definition_cls",
        "_step_execution_cls",
        "_step_section_begin_cls",
        "_step_section_description_cls",
        "_step_section_end_cls",
    ]

    def __init__(self):  # type: (...) -> None
        """
        Declares fast path data.
        """
        # Instances.

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
        #: Instantiated by :meth:`reflection_logger()` property.
        #:
        #: .. note:: Not instantiated in :mod:`._reflection`, but here with this :class:`FastPath` class.
        self._reflection_logger = None  # type: typing.Optional[_LoggerType]

        #: :class:`._args.Args` instance installed.
        #:
        #: Reference set by :meth:`._args.Args.setinstance()` via the :meth:`args()` setter.
        self._args = None  # type: typing.Optional[_ArgsType]

        #: :class:`._scenarioargs.CommonExecArgs` instance installed.
        #:
        #: Reference set by :meth:`._args.Args.setinstance()` via the :meth:`args()` setter.
        self._exec_args = None  # type: typing.Optional[_CommonExecArgsType]

        #: :class:`._scenarioargs.ScenarioArgs` instance installed.
        #:
        #: Reference set by :meth:`._args.Args.setinstance()` via the :meth:`args()` setter.
        self._scenario_args = None  # type: typing.Optional[_ScenarioArgsType]

        #: :class:`._campaignargs.CampaignArgs` instance installed.
        #:
        #: Reference set by :meth:`._args.Args.setinstance()` via the :meth:`args()` setter.
        self._campaign_args = None  # type: typing.Optional[_CampaignArgsType]

        #: :class:`._configdb.ConfigDatabase` singleton reference.
        #:
        #: Reference resolved by :meth:`config_db()` property.
        self._config_db = None  # type: typing.Optional[_ConfigDatabaseType]

        #: :class:`._scenarioconfig.ScenarioConfig` singleton reference.
        #:
        #: Reference resolved by :meth:`scenario_config()` property.
        self._scenario_config = None  # type: typing.Optional[_ScenarioConfigType]

        #: :class:`._scenariorunner.ScenarioRunner` singleton reference.
        #:
        #: Reference resolved by :meth:`scenario_runner()` property.
        self._scenario_runner = None  # type: typing.Optional[_ScenarioRunnerType]

        #: :class:`._scenariostack.ScenarioStack` singleton reference.
        #:
        #: Reference resolved by :meth:`scenario_stack()` property.
        self._scenario_stack = None  # type: typing.Optional[_ScenarioStackType]

        #: :class:`._scenariologging.ScenarioLogging` singleton reference.
        #:
        #: Reference resolved by :meth:`scenario_logging()` property.
        self._scenario_logging = None  # type: typing.Optional[_ScenarioLoggingType]

        #: :class:`._campaignrunner.CampaignRunner` singleton reference.
        #:
        #: Reference resolved by :meth:`campaign_runner()` property.
        self._campaign_runner = None  # type: typing.Optional[_CampaignRunnerType]

        #: :class:`._campaignlogging.CampaignLogging` singleton reference.
        #:
        #: Reference resolved by :meth:`campaign_logging()` property.
        self._campaign_logging = None  # type: typing.Optional[_CampaignLoggingType]

        #: :class:`._handlers.Handlers` singleton reference.
        #:
        #: Reference resolved by :meth:`handlers()` property.
        self._handlers = None  # type: typing.Optional[_HandlersType]

        #: :class:`._reqdb.ReqDatabase` singleton reference.
        #:
        #: Reference resolved by :meth:`req_db()` property.
        self._req_db = None  # type: typing.Optional[_ReqDatabaseType]

        # Classes.

        #: :class:`._scenariodefinition.ScenarioDefinition` class reference.
        #:
        #: Reference resolved by :meth:`scenario_definition_cls()` property.
        self._scenario_definition_cls = None  # type: typing.Optional[typing.Type[_ScenarioDefinitionType]]

        #: :class:`._scenarioexecution.ScenarioExecution` class reference.
        #:
        #: Reference resolved by :meth:`scenario_execution_cls()` property.
        self._scenario_execution_cls = None  # type: typing.Optional[typing.Type[_ScenarioExecutionType]]

        #: :class:`._stepdefinition.StepDefinition` class reference.
        #:
        #: Reference resolved by :meth:`step_definition_cls()` property.
        self._step_definition_cls = None  # type: typing.Optional[typing.Type[_StepDefinitionType]]

        #: :class:`._stepexecution.StepExecution` class reference.
        #:
        #: Reference resolved by :meth:`step_execution_cls()` property.
        self._step_execution_cls = None  # type: typing.Optional[typing.Type[_StepExecutionType]]

        #: :class:`._stepsection.StepSectionDescription` class reference.
        #:
        #: Reference resolved by :meth:`step_section_description_cls()` property.
        self._step_section_description_cls = None  # type: typing.Optional[typing.Type[_StepSectionDescriptionType]]

        #: :class:`._stepsection.StepSectionBegin` class reference.
        #:
        #: Reference resolved by :meth:`step_section_begin_cls()` property.
        self._step_section_begin_cls = None  # type: typing.Optional[typing.Type[_StepSectionBeginType]]

        #: :class:`._stepsection.StepSectionEnd` class reference.
        #:
        #: Reference resolved by :meth:`step_section_end_cls()` property.
        self._step_section_end_cls = None  # type: typing.Optional[typing.Type[_StepSectionEndType]]

        #: :class:`._actionresultdefinition.ActionResultDefinition` class reference.
        #:
        #: Reference resolved by :meth:`action_result_definition_cls()` property.
        self._action_result_definition_cls = None  # type: typing.Optional[typing.Type[_ActionResultDefinitionType]]

        #: :class:`._actionresultexecution.ActionResultExecution` class reference.
        #:
        #: Reference resolved by :meth:`action_result_execution_cls()` property.
        self._action_result_execution_cls = None  # type: typing.Optional[typing.Type[_ActionResultExecutionType]]

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

        #: :class:`._reqlink.ReqLink` class reference.
        #:
        #: Reference resolved by :meth:`req_link_cls()` property.
        self._req_link_cls = None  # type: typing.Optional[typing.Type[_ReqLinkType]]

        #: :class:`._reqlink.ReqLinkHelper` class reference.
        #:
        #: Reference resolved by :meth:`req_link_helper_cls()` property.
        self._req_link_helper_cls = None  # type: typing.Optional[typing.Type[_ReqLinkHelperType]]

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
    def args(self):  # type: () -> typing.Optional[_ArgsType]
        """
        :class:`._args.Args` instance installed, if any.
        """
        return self._args

    @args.setter
    def args(self, args):  # type: (typing.Optional[_ArgsType]) -> None
        """
        :class:`._args.Args` instance setter.
        """
        from ._args import Args  # check-imports: ignore  ## `FastPath` local import.
        from ._campaignargs import CampaignArgs  # check-imports: ignore  ## `FastPath` local import.
        from ._scenarioargs import CommonExecArgs, ScenarioArgs  # check-imports: ignore  ## `FastPath` local import.

        self._args = args
        self._exec_args = args if (isinstance(args, Args) and isinstance(args, CommonExecArgs)) else None
        self._scenario_args = args if isinstance(args, ScenarioArgs) else None
        self._campaign_args = args if isinstance(args, CampaignArgs) else None

    @property
    def exec_args(self):  # type: () -> typing.Optional[_CommonExecArgsType]
        """
        :class:`._scenarioargs.CommonExecArgs` instance installed, if any.
        """
        return self._exec_args

    @property
    def scenario_args(self):  # type: () -> typing.Optional[_ScenarioArgsType]
        """
        :class:`._scenarioargs.ScenarioArgs` instance installed, if any.
        """
        return self._scenario_args

    @property
    def campaign_args(self):  # type: () -> typing.Optional[_CampaignArgsType]
        """
        :class:`._campaignargs.CampaignArgs` instance installed, if any.
        """
        return self._campaign_args

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
    def scenario_runner(self):  # type: () -> _ScenarioRunnerType
        """
        :class:`._scenariorunner.ScenarioRunner` singleton.
        """
        if self._scenario_runner is None:
            from ._scenariorunner import SCENARIO_RUNNER  # check-imports: ignore  ## `FastPath` local import.
            self._scenario_runner = SCENARIO_RUNNER
        return self._scenario_runner

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
    def scenario_logging(self):  # type: (...) -> _ScenarioLoggingType
        """
        :class:`._scenariologging.ScenarioLogging` singleton.
        """
        if self._scenario_logging is None:
            from ._scenariologging import SCENARIO_LOGGING  # check-imports: ignore  ## `FastPath` local import.
            self._scenario_logging = SCENARIO_LOGGING
        return self._scenario_logging

    @property
    def campaign_runner(self):  # type: () -> _CampaignRunnerType
        """
        :class:`._campaignrunner.CampaignRunner` singleton.
        """
        if self._campaign_runner is None:
            from ._campaignrunner import CAMPAIGN_RUNNER  # check-imports: ignore  ## `FastPath` local import.
            self._campaign_runner = CAMPAIGN_RUNNER
        return self._campaign_runner

    @property
    def campaign_logging(self):  # type: () -> _CampaignLoggingType
        """
        :class:`._campaignlogging.CampaignLogging` singleton.
        """
        if self._campaign_logging is None:
            from ._campaignlogging import CAMPAIGN_LOGGING  # check-imports: ignore  ## `FastPath` local import.
            self._campaign_logging = CAMPAIGN_LOGGING
        return self._campaign_logging

    @property
    def handlers(self):  # type: () -> _HandlersType
        """
        :class:`._handlers.Handlers` singleton.
        """
        if self._handlers is None:
            from ._handlers import HANDLERS  # check-imports: ignore  ## `FastPath` local import.
            self._handlers = HANDLERS
        return self._handlers

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
    def scenario_execution_cls(self):  # type: () -> typing.Type[_ScenarioExecutionType]
        """
        :class:`._scenarioexecution.ScenarioExecution` class reference.
        """
        if self._scenario_execution_cls is None:
            from ._scenarioexecution import ScenarioExecution  # check-imports: ignore  ## `FastPath` local import.
            self._scenario_execution_cls = ScenarioExecution
        return self._scenario_execution_cls

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
    def step_execution_cls(self):  # type: () -> typing.Type[_StepExecutionType]
        """
        :class:`._stepexecution.StepExecution` class reference.
        """
        if self._step_execution_cls is None:
            from ._stepexecution import StepExecution  # check-imports: ignore  ## `FastPath` local import.
            self._step_execution_cls = StepExecution
        return self._step_execution_cls

    @property
    def step_section_description_cls(self):  # type: () -> typing.Type[_StepSectionDescriptionType]
        """
        :class:`._stepsection.StepSectionDescription` class reference.
        """
        if self._step_section_description_cls is None:
            from ._stepsection import StepSectionDescription  # check-imports: ignore  ## `FastPath` local import.
            self._step_section_description_cls = StepSectionDescription
        return self._step_section_description_cls

    @property
    def step_section_begin_cls(self):  # type: () -> typing.Type[_StepSectionBeginType]
        """
        :class:`._stepsection.StepSectionBegin` class reference.
        """
        if self._step_section_begin_cls is None:
            from ._stepsection import StepSectionBegin  # check-imports: ignore  ## `FastPath` local import.
            self._step_section_begin_cls = StepSectionBegin
        return self._step_section_begin_cls

    @property
    def step_section_end_cls(self):  # type: () -> typing.Type[_StepSectionEndType]
        """
        :class:`._stepsection.StepSectionEnd` class reference.
        """
        if self._step_section_end_cls is None:
            from ._stepsection import StepSectionEnd  # check-imports: ignore  ## `FastPath` local import.
            self._step_section_end_cls = StepSectionEnd
        return self._step_section_end_cls

    @property
    def action_result_definition_cls(self):  # type: () -> typing.Type[_ActionResultDefinitionType]
        """
        :class:`._actionresultdefinition.ActionResultDefinition` class reference.
        """
        if self._action_result_definition_cls is None:
            from ._actionresultdefinition import ActionResultDefinition  # check-imports: ignore  ## `FastPath` local import.
            self._action_result_definition_cls = ActionResultDefinition
        return self._action_result_definition_cls

    @property
    def action_result_execution_cls(self):  # type: () -> typing.Type[_ActionResultExecutionType]
        """
        :class:`._actionresultexecution.ActionResultExecution` class reference.
        """
        if self._action_result_execution_cls is None:
            from ._actionresultexecution import ActionResultExecution  # check-imports: ignore  ## `FastPath` local import.
            self._action_result_execution_cls = ActionResultExecution
        return self._action_result_execution_cls

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

    @property
    def req_link_cls(self):  # type: () -> typing.Type[_ReqLinkType]
        """
        #: :class:`._reqlink.ReqLink` class reference.
        """
        if self._req_link_cls is None:
            from ._reqlink import ReqLink  # check-imports: ignore  ## `FastPath` local import.
            self._req_link_cls = ReqLink
        return self._req_link_cls

    @property
    def req_link_helper_cls(self):  # type: () -> typing.Type[_ReqLinkHelperType]
        """
        #: :class:`._reqlink.ReqLinkHelper` class reference.
        """
        if self._req_link_helper_cls is None:
            from ._reqlink import ReqLinkHelper  # check-imports: ignore  ## `FastPath` local import.
            self._req_link_helper_cls = ReqLinkHelper
        return self._req_link_helper_cls


#: Main instance of :class:`FastPath`.
FAST_PATH = FastPath()
