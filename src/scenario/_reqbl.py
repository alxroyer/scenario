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
Requirement baseline management.
"""

import typing

if True:
    from ._debugclasses import DebugClass as _DebugClassImpl  # @perf
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
    from ._scenariodefinition import ScenarioDefinitionHelper as _ScenarioDefinitionHelperImpl  # @perf
if typing.TYPE_CHECKING:
    from ._path import Path as _PathType
    from ._reqdb import ReqDatabase as _ReqDatabaseType
    from ._scenariodefinition import ScenarioDefinition as _ScenarioDefinitionType


class ReqBaseline(_LoggerImpl):
    """
    Requirement baseline.

    Holds a requirement database, and a list of scenarios verifying the requirements stored in the database.

    When used as a context, the requirement baseline registers itself with the :class:`._scenariostack.ScenarioStack`,
    so that :class:`._req.Req`, :class:`._reqref.ReqRef`, :class:`._reqverifier.ReqVerifier` (scenarios and steps) and :class:`._reqlink.ReqLink` objects
    know their related baseline / requirement database when they are instantiated.
    """

    def __init__(
            self,
            name,  # type: str
    ):  # type: (...) -> None
        """
        Initializes a baseline with empty :class:`._reqdb.ReqDatabase` and scenario list.

        :param name: Baseline name.
        """
        from ._reqdb import ReqDatabase

        _LoggerImpl.__init__(self, _DebugClassImpl.REQ_BASELINE)

        #: Baseline name.
        self.name = name  # type: str

        #: Requirement database.
        self.req_db = ReqDatabase(self)  # type: _ReqDatabaseType

        #: Scenarios verifying the requirements in :attr:`req_db`.
        #:
        #: Usually fed by :meth:`fromfiles()`,
        #: or :meth:`._campaignreport.CampaignReport.readcampaignreport()` when reading campaign results.
        #: Also fed by :meth:`._scenariorunner.ScenarioRunner.executepath()` and :meth:`._campaignrunner.CampaignRunner._exectestcase()`.
        self.scenarios = []  # type: typing.List[_ScenarioDefinitionType]

    def __enter__(self):  # type: (...) -> None
        """
        Registers the baseline in :class:`._scenariostack.ScenarioStack` as the applicable one.
        """
        _FAST_PATH.scenario_stack.reqs.pushbaseline(self)

    def __exit__(
            self,
            exc_type,  # type: typing.Any
            exc_val,  # type: typing.Any
            exc_tb,  # type: typing.Any
    ):  # type: (...) -> None
        """
        Unregisters the baseline from :class:`._scenariostack.ScenarioStack`.
        """
        _FAST_PATH.scenario_stack.reqs.popbaseline(self)

    @staticmethod
    def fromfiles(
            name,  # type: str
            *,
            req_db_paths=None,  # type: typing.Optional[typing.Iterable[_PathType]]
            test_suite_paths=None,  # type: typing.Optional[typing.Iterable[_PathType]]
            log_info=True,  # type: bool
    ):  # type: (...) -> ReqBaseline
        """
        Builds a :class:`ReqBaseline` instance,
        and loads input data from requirement and/or test suite files.

        :param name:
            Name for the new :class:`ReqBaseline` instance.
        :param req_db_paths:
            Optional requirement database files to load.

            If empty set, no requirements are loaded.

            If ``None``, the :attr:`._scenarioconfig.ScenarioConfig.Key.REQ_DB_FILES` configuration is taken into account.
        :param test_suite_paths:
            Optional test suite files to load scenarios from.

            If empty set, no scenarios are loaded.

            If ``None``, the :attr:`._scenarioconfig.ScenarioConfig.Key.TEST_SUITE_FILES` configuration will be taken into account.
        :param log_info:
            ``True`` (by default) to generate info logging.
        :return:
            Requirement baseline loaded with requirements and scenarios.
        """
        from ._testsuitefile import TestSuiteFile

        # Build the `ReqBaseline` instance.
        _req_baseline = ReqBaseline(name)  # type: ReqBaseline
        with _req_baseline:
            _req_baseline.debug("ReqBaseline.fromfiles(req_db_paths=%r, test_suite_paths=%r, log_info=%r)", req_db_paths, test_suite_paths, log_info)

            # Requirements.

            if req_db_paths is not None:
                # Ensure persistent and countable sequence.
                req_db_paths = tuple(req_db_paths)
            else:
                # Default configuration.
                req_db_paths = _FAST_PATH.scenario_config.reqdbpaths()

            if req_db_paths:
                if log_info:
                    _FAST_PATH.main_logger.info("Loading requirements")
                with _FAST_PATH.main_logger.pushindentation("  " if log_info else ""):
                    _req_baseline.debug("Reading %d req-db file(s)", len(list(req_db_paths)))
                    for _req_db_file_path in req_db_paths:  # type: _PathType
                        if log_info:
                            _FAST_PATH.main_logger.info(f"Loading '{_req_db_file_path}'")
                        _req_baseline.req_db.load(_req_db_file_path)

                if log_info:
                    _req_ref_count = len(_req_baseline.req_db.getallrefs())  # type: int
                    _FAST_PATH.main_logger.info(f"{_req_ref_count} requirement reference{'' if (_req_ref_count == 1) else 's'} loaded")

            # Scenarios.

            if test_suite_paths is not None:
                # Ensure persistent and countable sequence.
                test_suite_paths = tuple(test_suite_paths)
            else:
                # Default configuration.
                test_suite_paths = _FAST_PATH.scenario_config.testsuitepaths()

            if test_suite_paths:
                if log_info:
                    _FAST_PATH.main_logger.info("Loading scenarios")
                with _FAST_PATH.main_logger.pushindentation("  " if log_info else ""):
                    try:
                        # Disable scenario debug logging.
                        _initial_scenario_debug_logging = (
                            _FAST_PATH.config_db.get(_FAST_PATH.scenario_config.Key.SCENARIO_DEBUG_LOGGING_ENABLED, type=bool)
                        )  # type: typing.Optional[bool]
                        _FAST_PATH.config_db.set(_FAST_PATH.scenario_config.Key.SCENARIO_DEBUG_LOGGING_ENABLED, False)

                        _req_baseline.debug("Reading %d test suite file(s)", len(list(test_suite_paths)))
                        for _test_suite_path in test_suite_paths:  # type: _PathType
                            if log_info:
                                _FAST_PATH.main_logger.info("Loading '%s'", _test_suite_path)
                            with _FAST_PATH.main_logger.pushindentation("  " if log_info else ""):
                                _test_suite_file = TestSuiteFile(_test_suite_path)  # type: TestSuiteFile
                                _test_suite_file.read()
                                for _test_script_path in _test_suite_file.script_paths:  # type: _PathType
                                    if log_info:
                                        _FAST_PATH.main_logger.info("Loading '%s'", _test_script_path)

                                    # Find the scenario class.
                                    _scenario_definition_class = _ScenarioDefinitionHelperImpl.getscenariodefinitionclassfromscript(
                                        _test_script_path,
                                        # Avoid loaded module being saved in `sys.modules`,
                                        # so that the function can be called again, and traceability refreshed.
                                        sys_modules_cache=False,
                                    )  # type: typing.Type[_ScenarioDefinitionType]
                                    _req_baseline.debug("_scenario_definition_class=%r", _scenario_definition_class)

                                    # Create the scenario instance.
                                    _scenario = _scenario_definition_class()  # type: _ScenarioDefinitionType
                                    _req_baseline.debug("_scenario=%r", _scenario)
                                    _req_baseline.scenarios.append(_scenario)
                    finally:
                        # Restore initial scenario debug logging configuration.
                        _FAST_PATH.config_db.set(_FAST_PATH.scenario_config.Key.SCENARIO_DEBUG_LOGGING_ENABLED, _initial_scenario_debug_logging)

                if log_info:
                    _scenario_count = len(_req_baseline.scenarios)  # type: int
                    _FAST_PATH.main_logger.info(f"{_scenario_count} scenario{'' if (_scenario_count == 1) else 's'} loaded")

        return _req_baseline

    @staticmethod
    def fromcampaignresults(
            campaign_results_path,  # type: _PathType
            *,
            name=None,  # type: typing.Optional[str]
            log_info=True,  # type: bool
    ):  # type: (...) -> ReqBaseline
        """
        Builds a :class:`ReqBaseline` instance,
        and loads input data from campaign execution results.

        :param campaign_results_path: Path of campaign results, either the directory or the campaign report path.
        :param name: Optional name. Determined from ``campaign_results_path`` otherwise.
        :param log_info: ``True`` (by default) to generate info logging.
        :return: Requirement baseline loaded with requirements and scenarios.
        """
        from ._campaignexecution import CampaignExecution

        # Build the `ReqBaseline` instance.
        _req_baseline = ReqBaseline(name=name or campaign_results_path.prettypath)  # type: ReqBaseline

        _req_baseline.debug("ReqBaseline.fromcampaignresults(campaign_results='%s', name=%r, log_info=%r)", campaign_results_path, name, log_info)

        # Determine the path of the campaign report file.
        _campaign_report_path = campaign_results_path  # type: _PathType
        if _campaign_report_path.is_dir():
            _campaign_report_path = CampaignExecution(_campaign_report_path).campaign_report_path
            if not _campaign_report_path.is_file():
                raise FileNotFoundError(f"No campaign file found in '{campaign_results_path}'")

        _req_baseline.debug("Campaign report file: '%s'", _campaign_report_path)

        if log_info:
            _FAST_PATH.main_logger.info(f"Loading campaign results from '{_campaign_report_path}'")
        _campaign_execution = _FAST_PATH.campaign_report.readcampaignreport(
            _campaign_report_path,
            req_baseline=_req_baseline,
            read_scenario_reports=True,  # Read scenario reports in order to feed the requirement baseline with scenarios.
        )  # type: CampaignExecution

        # Adjust the baseline name from the campaign name (unless the name had been explicitly specified).
        if name is None:
            _req_baseline.name = _campaign_execution.name

        if log_info:
            _req_ref_count = len(_req_baseline.req_db.getallrefs())  # type: int
            _FAST_PATH.main_logger.info(f"{_req_ref_count} requirement reference{'' if (_req_ref_count == 1) else 's'} loaded")
            _scenario_count = len(_req_baseline.scenarios)  # type: int
            _FAST_PATH.main_logger.info(f"{_scenario_count} scenario{'' if (_scenario_count == 1) else 's'} loaded")

        return _req_baseline
