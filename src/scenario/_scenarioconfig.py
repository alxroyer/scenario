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
`scenario` framework configurations.
"""

import typing

if True:
    from . import _consoleutils as _consoleutils  # @perf
    from . import _enumutils as _enumutils  # @inheritance
    from ._debugclasses import DebugClass as _DebugClassImpl  # @perf
    from ._fastpath import FAST_PATH as _FAST_PATH  # @perf
    from ._issuelevels import IssueLevel as _IssueLevelImpl  # @perf
    from ._logger import Logger as _LoggerImpl  # @inheritance
    from ._path import Path as _PathImpl  # @perf
    from ._path import ROOT_SCENARIO_PATH as _ROOT_SCENARIO_PATH  # @perf
if typing.TYPE_CHECKING:
    from ._campaignargs import CampaignArgs as _CampaignArgsType
    from ._confignode import ConfigNode as _ConfigNodeType
    from ._issuelevels import AnyIssueLevelType as _AnyIssueLevelType
    from ._path import Path as _PathType


class ScenarioConfig(_LoggerImpl):
    """
    `scenario` configuration management.

    Instantiated once with the :data:`SCENARIO_CONFIG` singleton.

    This class defines methods that help reading `scenario` configurations:
    from the program arguments (see: :class:`._args.Args`),
    and the configuration database (see: :class:`._configdb.ConfigDatabase`).
    """

    class Key(_enumutils.StrEnum):
        """
        `scenario` configuration keys.
        """

        # Time & logging.

        #: Should a specific timezone be used? String value. Default is the local timezone.
        TIMEZONE = "scenario.timezone"
        #: Should the log lines include a timestamp? Boolean value.
        LOG_DATETIME = "scenario.log_datetime"
        #: Should the log lines be displayed in the console? Boolean value.
        LOG_CONSOLE = "scenario.log_console"
        #: Should the log lines be colored? Boolean value.
        LOG_COLOR_ENABLED = "scenario.log_color"
        #: Log color per log level. Integer value.
        LOG_COLOR = "scenario.log_%s_color"
        #: Should the log lines be written in a log file? Absolute path string.
        LOG_FILE = "scenario.log_file"
        #: Which debug classes to display? List of strings, or comma-separated string.
        DEBUG_CLASSES = "scenario.debug_classes"
        #: Should scenario debug logging be enabled by default? Boolean value.
        SCENARIO_DEBUG_LOGGING_ENABLED = "scenario.scenario_debug_logging_enabled"

        # Requirement management.

        #: Default requirement files. List of absolute path strings, or comma-separated string.
        REQ_DB_FILES = "scenario.req_db_files"
        #: Should the scenario requirement coverage be refined on steps? Boolean value.
        EXPECT_STEP_REQ_REFINEMENT = "scenario.expect_step_req_refinement"

        # Test & campaign execution.

        #: Expected scenario attributes. List of strings, or comma-separated string.
        EXPECTED_SCENARIO_ATTRIBUTES = "scenario.expected_scenario_attributes"
        #: Should the scenario continue on error? Boolean value.
        CONTINUE_ON_ERROR = "scenario.continue_on_error"
        #: Should we wait between two step executions? Float value.
        DELAY_BETWEEN_STEPS = "scenario.delay_between_steps"
        #: Runner script path. Absolute path string. Default is 'bin/run-test.py' in the :mod:`scenario` repository directory.
        RUNNER_SCRIPT_PATH = "scenario.runner_script_path"
        #: Default test suite files. List of absolute path strings, or comma-separated string.
        TEST_SUITE_FILES = "scenario.test_suite_files"
        #: Maximum time for a scenario execution. Useful when executing campaigns. Float value in seconds.
        SCENARIO_TIMEOUT = "scenario.scenario_timeout"

        # Results & reports.

        #: Scenario attributes to display for extra info when displaying scenario results,
        #: after a campaign execution, or when executing several tests in a single command line.
        #: List of strings, or comma-separated string.
        RESULTS_EXTRA_INFO = "scenario.results_extra_info"
        #: Campaign output directory path. Absolute path string. Defaults to the current working directory.
        CAMPAIGN_OUTDIR = "scenario.campaign_dir"
        #: Campaign output subdirectory mode. One of :class:`._campaignargs.CampaignArgs.SubdirMode`.
        CAMPAIGN_SUBDIR_MODE = "scenario.campaign_subdir_mode"
        #: Scenario report suffix when writing campaign results. Default is '.json'.
        SCENARIO_REPORT_SUFFIX = "scenario.scenario_report_suffix"
        #: Campaign report file name used when reading / writing campaign results. String value. Default is 'campaign.xml'.
        CAMPAIGN_REPORT_FILENAME = "scenario.campaign_report_filename"
        #: Requirement database file name used when reading / writing campaign results. String value. Default is 'req-db-json'.
        REQ_DB_FILENAME = "scenario.req_db_filename"
        #: Downstream traceability report file name used when reading / writing campaign results. String value. Default is 'req-downstream-traceability.json'.
        DOWNSTREAM_TRACEABILITY_FILENAME = "scenario.downstream_traceability_filename"
        #: Upstream traceability report file name used when reading / writing campaign results. String value. Default is 'req-upstream-traceability.json'.
        UPSTREAM_TRACEABILITY_FILENAME = "scenario.upstream_traceability_filename"

        # Known issues and issue levels.

        #: Issue level names. Dictionary of names (``str``) => ``int`` values.
        ISSUE_LEVEL_NAMES = "scenario.issue_levels"
        #: Issue level from and above which known issues should be considered as errors.
        ISSUE_LEVEL_ERROR = "scenario.issue_level_error"
        #: Issue level from and under which known issues should be ignored.
        ISSUE_LEVEL_IGNORED = "scenario.issue_level_ignored"

    def __init__(self):  # type: (...) -> None
        """
        Initializes the instance as a logger, and the timezone cache information.
        """
        _LoggerImpl.__init__(self, _DebugClassImpl.SCENARIO_CONFIG)

        #: Timezone cache information.
        self.__timezone = None  # type: typing.Optional[str]

    def timezone(self):  # type: (...) -> typing.Optional[str]
        """
        Gives the timezone configuration, if set.

        :return:
            Timezone configuration if set, ``None`` otherwise.

            When not set, the local timezone is used.
        """
        if self.__timezone is None:
            # Set the cache member with an empty string if no configuration is set.
            self.__timezone = _FAST_PATH.config_db.get(self.Key.TIMEZONE, type=str, default="").strip()
            # Convert empty string to `None`.
            self.__timezone = self.__timezone or None

        # Don't debug `timezone()`, otherwise it may cause infinite recursions when logging.
        # self.debug("timezone() -> %r", self.__timezone)
        return self.__timezone

    def invalidatetimezonecache(self):  # type: (...) -> None
        """
        Invalidates the timezone cache information.
        """
        self.__timezone = None
        # Don't debug `invalidatetimezonecache()`, otherwise it may cause infinite recursions when logging (tbc).
        # self.debug("Timezone invalidated!")

    def logdatetimeenabled(self):  # type: (...) -> bool
        """
        Determines whether the Log line should include a timestamp.

        Configurable through :const:`Key.LOG_DATETIME`.
        """
        _log_datetime_enabled = _FAST_PATH.config_db.get(self.Key.LOG_DATETIME, type=bool, default=True)  # type: bool
        # Don't debug `logdatetimeenabled()`, otherwise it may cause infinite recursions when logging.
        # self.debug("logdatetimeenabled() -> %r", _log_datetime_enabled)
        return _log_datetime_enabled

    def logconsoleenabled(self):  # type: (...) -> bool
        """
        Determines whether the log should be displayed in the console.

        Configurable through :const:`Key.LOG_CONSOLE`.
        """
        _log_console_enabled = _FAST_PATH.config_db.get(self.Key.LOG_CONSOLE, type=bool, default=True)  # type: bool
        # Don't debug `logconsoleenabled()`, otherwise it may cause infinite recursions when logging.
        # self.debug("logconsoleenabled() -> %r", _log_console_enabled)
        return _log_console_enabled

    def logoutpath(self):  # type: (...) -> typing.Optional[_PathType]
        """
        Determines whether the log lines should be written in a log file.

        :return: Output log file path if set, ``None`` indicates no file logging.

        Configurable through :const:`Key.LOG_FILE`.
        """
        _log_outpath = None  # type: typing.Optional[_PathType]
        _config = _FAST_PATH.config_db.get(self.Key.LOG_FILE, type=str)  # type: typing.Optional[str]
        if _config:  # Neither `None` nor empty!
            _log_outpath = _PathImpl(_config)

        # Don't debug `logoutpath()`, otherwise it may cause infinite recursions when logging (tbc).
        # self.debug("logoutpath() -> %r", _log_outpath)
        return _log_outpath

    def logcolorenabled(self):  # type: (...) -> bool
        """
        Determines whether log colors should be used when displayed in the console.

        Configurable through :const:`Key.LOG_COLOR_ENABLED`.
        """
        _log_color_enabled = _FAST_PATH.config_db.get(self.Key.LOG_COLOR_ENABLED, type=bool, default=True)  # type: bool
        # Don't debug `logcolorenabled()`, otherwise it may cause infinite recursions when logging.
        # self.debug("logcolorenabled() -> %r", _log_color_enabled)
        return _log_color_enabled

    def logcolor(
            self,
            level,  # type: str
            default,  # type: _consoleutils.Console.Color
    ):  # type: (...) -> _consoleutils.Console.Color
        """
        Retrieves the expected log color for the given log level.

        :param level: Log level name.
        :param default: Default log color.
        :return: Log color configured, or default if not set.

        Configurable through :attr:`Key.LOG_COLOR`.
        """
        _key = str(self.Key.LOG_COLOR) % level.lower()  # type: str
        _config_node = _FAST_PATH.config_db.getnode(_key)  # type: typing.Optional[_ConfigNodeType]
        if _config_node:
            try:
                _color_number = _config_node.cast(type=int)  # type: int
                # Don't debug `logcolor()`, otherwise it may cause infinite recursions when logging.
                # self.debug("logcolor(level=%r, default=%r) -> %r", level, default, Console.Color(_color_number))
                return _consoleutils.Console.Color(_color_number)
            except ValueError:
                self.warning(_config_node.errmsg(f"Invalid color number {_config_node.data!r}"))
        # Don't debug `logcolor()`, otherwise it may cause infinite recursions when logging.
        # self.debug("logcolor(level=%r, default=%r) -> %r (default)", level, default, default)
        return default

    def debugclasses(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the debug classes configured.

        :return: List of debug classes.

        Adds debug classes defined by the program arguments (see :attr:`._loggingargs.CommonLoggingArgs.debug_classes`)
        plus those defined by the configurations (see :const:`Key.DEBUG_CLASSES`).
        """
        # Merge debug classes from...
        _debug_classes = []  # type: typing.List[str]
        # ...arguments,
        if _FAST_PATH.args:
            for _debug_class in _FAST_PATH.args.getinstance().debug_classes:  # type: str
                if _debug_class not in _debug_classes:
                    _debug_classes.append(_debug_class)
        # ...and configuration database.
        for _debug_class, _ in self._readstringlistfromconf(self.Key.DEBUG_CLASSES):  # Type already declared above.
            if _debug_class not in _debug_classes:
                _debug_classes.append(_debug_class)
        # Don't debug `debugclasses()`, otherwise it may cause infinite recursions when logging.
        # self.debug("debugclasses() -> %r", _debug_classes)
        return _debug_classes

    def scenariodebugloggingenabled(self):  # type: (...) -> bool
        """
        Tells whether scenario should enable debug logging.

        :return: ``True`` (default) enables scenario debug logging, ``False`` not.

        Configurable through :attr:`Key.SCENARIO_DEBUG_LOGGING_ENABLED`.
        """
        _debug_logging_enabled = _FAST_PATH.config_db.get(ScenarioConfig.Key.SCENARIO_DEBUG_LOGGING_ENABLED, type=bool, default=True)  # type: bool
        self.debug("scenariodebugloggingenabled() -> %r", _debug_logging_enabled)
        return _debug_logging_enabled

    def reqdbpaths(self):  # type: (...) -> typing.Sequence[_PathType]
        """
        Retrieves the input requirement files to load.

        :return: Sequence of requirement file paths.
        """
        # Determine requirement files from...
        _req_db_paths = []  # type: typing.List[_PathType]
        # ...requirement arguments first (when applicable),
        if _FAST_PATH.req_mgt_args:
            _req_db_paths.extend(_FAST_PATH.req_mgt_args.test_suite_paths)
        # ...or default configuration otherwise.
        if not _req_db_paths:
            _req_db_paths.extend(self._readpathlistfromconf(self.Key.REQ_DB_FILES))
        self.debug("reqdbpaths() -> %d files", len(_req_db_paths))
        for _req_db_path in _req_db_paths:  # type: _PathType
            self.debug(" -> %r", _req_db_path)
        return _req_db_paths

    def expectedscenarioattributes(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the user scenario expected attributes.

        Configurable through :attr:`Key.EXPECTED_SCENARIO_ATTRIBUTES`.
        """
        _attribute_names = []  # type: typing.List[str]
        for _attribute_name, _ in self._readstringlistfromconf(self.Key.EXPECTED_SCENARIO_ATTRIBUTES):  # type: str, _ConfigNodeType
            if _attribute_name not in _attribute_names:
                _attribute_names.append(_attribute_name)
        self.debug("expectedscenarioattributes() -> %r", _attribute_names)
        return _attribute_names

    def expectstepreqrefinement(self):  # type: (...) -> bool
        """
        Determines whether the scenario requirement coverage shall be refined on steps.

        Configurable through :const:`Key.EXPECT_STEP_REQ_REFINEMENT`.
        """
        _expect_step_req_refinement = _FAST_PATH.config_db.get(self.Key.EXPECT_STEP_REQ_REFINEMENT, type=bool, default=False)  # type: bool
        self.debug("expectstepreqrefinement() -> %r", _expect_step_req_refinement)
        return _expect_step_req_refinement

    def continueonerror(self):  # type: (...) -> bool
        """
        Determines whether the test should continue when a step ends in error.

        Configurable through :const:`Key.CONTINUE_ON_ERROR`.
        """
        _continue_on_error = _FAST_PATH.config_db.get(self.Key.CONTINUE_ON_ERROR, type=bool, default=False)  # type: bool
        self.debug("continueonerror() -> %r", _continue_on_error)
        return _continue_on_error

    def delaybetweensteps(self):  # type: (...) -> float
        """
        Retrieves the expected delay between steps.

        Checks in configurations only (see :attr:`Key.DELAY_BETWEEN_STEPS`).
        """
        _delay_between_steps = _FAST_PATH.config_db.get(self.Key.DELAY_BETWEEN_STEPS, type=float, default=0.001)  # type: float
        self.debug("delaybetweensteps() -> %r", _delay_between_steps)
        return _delay_between_steps

    def runnerscriptpath(self):  # type: (...) -> _PathType
        """
        Gives the path of the scenario runner script path.

        Useful when executing campaigns.
        """
        # Note: Using the `or` fallback below ensures our default value will hide empty strings.
        _abspath = (
            _FAST_PATH.config_db.get(self.Key.RUNNER_SCRIPT_PATH, type=str)
            or (_ROOT_SCENARIO_PATH / "bin" / "run-test.py").abspath
        )  # type: str
        self.debug("runnerscriptpath() -> %r", _PathImpl(_abspath))
        return _PathImpl(_abspath)

    def testsuitepaths(self):  # type: (...) -> typing.Sequence[_PathType]
        """
        Retrieves the input test suite files to load.

        Useful for campaign execution or requirement management.

        Read from campaign arguments (when applicable), or :attr:`ScenarioConfig.Key.TEST_SUITE_FILES` default configuration.

        :return: Sequence of tTest suite file paths.
        """
        # Determine test suite files from...
        _test_suite_paths = []  # type: typing.List[_PathType]
        # ...campaign or requirement arguments first (when applicable),
        if _FAST_PATH.campaign_args:
            _test_suite_paths.extend(_FAST_PATH.campaign_args.test_suite_paths)
        if _FAST_PATH.req_mgt_args:
            _test_suite_paths.extend(_FAST_PATH.req_mgt_args.test_suite_paths)
        # ...or default configuration otherwise.
        if not _test_suite_paths:
            _test_suite_paths.extend(self._readpathlistfromconf(self.Key.TEST_SUITE_FILES))
        self.debug("testsuitepaths() -> %d files", len(_test_suite_paths))
        for _test_suite_path in _test_suite_paths:  # type: _PathType
            self.debug(" -> %r", _test_suite_path)
        return _test_suite_paths

    def scenariotimeout(self):  # type: (...) -> float
        """
        Retrieves the maximum time for a scenario execution.

        Useful when executing campaigns.

        Checks in configurations only (see :attr:`Key.SCENARIO_TIMEOUT`).
        """
        _scenario_timeout = _FAST_PATH.config_db.get(self.Key.SCENARIO_TIMEOUT, type=float, default=600.0)  # type: float
        self.debug("scenariotimeout() -> %r", _scenario_timeout)
        return _scenario_timeout

    def resultsextrainfo(self):  # type: (...) -> typing.Sequence[str]
        """
        Retrieves the list of scenario attributes to display for extra info when displaying test results.

        :return: List of scenario attribute names.

        Applicable when displaying campaign results,
        or the result of several tests executed in a single command line.

        Returns a 1-item list with :attr:`._scenarioattributes.CoreScenarioAttributes.TITLE`
        by default in case nothing is configured.
        """
        from ._scenarioattributes import CoreScenarioAttributes

        # Merge attribute names from...
        _attribute_names = set()  # type: typing.Set[str]
        # ...arguments,
        if _FAST_PATH.scenario_args:
            _attribute_names.update(_FAST_PATH.scenario_args.extra_info)
        if _FAST_PATH.campaign_args:
            _attribute_names.update(_FAST_PATH.campaign_args.extra_info)
        # ...and configuration database.
        for _attribute_name, _ in self._readstringlistfromconf(self.Key.RESULTS_EXTRA_INFO):  # Type already declared above.
            _attribute_names.add(_attribute_name)

        # Default to titles.
        if not _attribute_names:
            _attribute_names.add(CoreScenarioAttributes.TITLE)

        self.debug("resultsextrainfo() -> %r", _attribute_names)
        return list(_attribute_names)

    def campaignoutdir(self):  # type: (...) -> _PathType
        """
        Campaign output directory.

        Read from campaign arguments,
        or from configurations,
        or defaults to current working directory.
        """
        _outdir = _PathImpl()  # type: _PathType
        # Read from campaign arguments first.
        if _FAST_PATH.campaign_args and _FAST_PATH.campaign_args.outdir:
            _outdir = _FAST_PATH.campaign_args.outdir
        # Then read from configuration database.
        if not _outdir:
            _outdir = _PathImpl(_FAST_PATH.config_db.get(self.Key.CAMPAIGN_OUTDIR, type=str, default=None))
        # Default to current working directory.
        if not _outdir:
            _outdir = _PathImpl.cwd()

        self.debug("campaignoutdir() -> %r", _outdir)
        return _outdir

    def campaignsubdirmode(self):  # type: (...) -> _CampaignArgsType.SubdirMode
        """
        Campaign output subdirectory mode.

        Read from campaign arguments,
        or from configurations,
        or defaults to date/time subdirectory mode.
        """
        from ._campaignargs import CampaignArgs  # check-imports: ignore  ## `CampaignArgs` implementation required, even for default value.

        _subdir_mode = None  # type: typing.Optional[_CampaignArgsType.SubdirMode]
        # Read from campaign arguments first.
        if _FAST_PATH.campaign_args and _FAST_PATH.campaign_args.subdir_mode:
            _subdir_mode = _FAST_PATH.campaign_args.subdir_mode
        # Then read from configuration database.
        if (_subdir_mode is None) and _FAST_PATH.campaign_args:
            _subdir_mode = _FAST_PATH.config_db.get(self.Key.CAMPAIGN_SUBDIR_MODE, type=CampaignArgs.SubdirMode, default=None)
        # Default to date/time subdirectory mode.
        if _subdir_mode is None:
            _subdir_mode = CampaignArgs.SubdirMode.DATE_TIME

        self.debug("campaignsubdirmode() -> %r", _subdir_mode)
        return _subdir_mode

    def scenarioreportsuffix(self):  # type: (...) -> str
        """
        Scenario report suffix to use.

        Used when writing campaign results.

        '.json' by default.
        """
        # Note: Using the `or` fallback below ensures our default value will hide empty strings.
        _scenario_report_suffix = (
            _FAST_PATH.config_db.get(self.Key.SCENARIO_REPORT_SUFFIX, type=str)
            or ".json"
        )  # type: str
        self.debug("scenarioreportsuffix() -> %r", _scenario_report_suffix)
        return _scenario_report_suffix

    def campaignreportfilename(self):  # type: (...) -> str
        """
        Campaign report file name used when reading / writing campaign results.

        Used when reading or writing campaign results.

        'campaign.xml' by default.
        """
        # Note: Using the `or` fallback below ensures our default value will hide empty strings.
        _campaign_report_filename = (
            _FAST_PATH.config_db.get(self.Key.CAMPAIGN_REPORT_FILENAME, type=str)
            or "campaign.xml"
        )  # type: str
        self.debug("campaignreportfilename() -> %r", _campaign_report_filename)
        return _campaign_report_filename

    def reqdbfilename(self):  # type: (...) -> str
        """
        Requirement database file name.

        Used when reading or writing campaign results.

        Configurable through :const:`Key.REQ_DB_FILENAME`.
        """
        # Note: Using the `or` fallback below ensures our default value will hide empty strings.
        _req_db_filename = (
            _FAST_PATH.config_db.get(self.Key.REQ_DB_FILENAME, type=str)
            or "req-db.json"
        )  # type: str
        self.debug("reqdbfilename() -> %r", _req_db_filename)
        return _req_db_filename

    def downstreamtraceabilityfilename(self):  # type: (...) -> str
        """
        Downstream traceability report file name.

        Used when reading or writing campaign results.

        Configurable through :const:`Key.DOWNSTREAM_TRACEABILITY_FILENAME`.
        """
        # Note: Using the `or` fallback below ensures our default value will hide empty strings.
        _downstream_traceability_filename = (
            _FAST_PATH.config_db.get(self.Key.DOWNSTREAM_TRACEABILITY_FILENAME, type=str)
            or "req-downstream-traceability.json"
        )  # type: str
        self.debug("downstreamtraceabilityfilename() -> %r", _downstream_traceability_filename)
        return _downstream_traceability_filename

    def upstreamtraceabilityfilename(self):  # type: (...) -> str
        """
        Upstream traceability report file name.

        Used when reading or writing campaign results.

        Configurable through :const:`Key.UPSTREAM_TRACEABILITY_FILENAME`.
        """
        # Note: Using the `or` fallback below ensures our default value will hide empty strings.
        _upstream_traceability_filename = (
            _FAST_PATH.config_db.get(self.Key.UPSTREAM_TRACEABILITY_FILENAME, type=str)
            or "req-upstream-traceability.json"
        )  # type: str
        self.debug("upstreamtraceabilityfilename() -> %r", _upstream_traceability_filename)
        return _upstream_traceability_filename

    def loadissuelevelnames(self):  # type: (...) -> None
        """
        Loads the issue level names configured through configuration files.
        """
        _root_node = _FAST_PATH.config_db.getnode(self.Key.ISSUE_LEVEL_NAMES)  # type: typing.Optional[_ConfigNodeType]
        if _root_node:
            for _name in _root_node.getsubkeys():  # type: str
                # Retrieve the `int` value configured with the issue level name.
                _subnode = _root_node.get(_name)  # type: typing.Optional[_ConfigNodeType]
                assert _subnode, "Internal error"
                try:
                    _value = _subnode.cast(int)  # type: int
                except ValueError as _err:
                    self.warning(_subnode.errmsg(f"Not an integer value {_subnode.data!r}, issue level name ignored"))
                    continue

                # Check value consistency when the issue level name is already known.
                if _name in _IssueLevelImpl.getnamed():
                    if _value != _IssueLevelImpl.parse(_name):
                        self.warning(_subnode.errmsg(
                            f"Name already set {_IssueLevelImpl.getdesc(_IssueLevelImpl.parse(_name))}, issue level name {_name}={_value!r} ignored"
                        ))
                    continue

                # Save the association between the new issue level name and value.
                self.debug("loadissuelevelnames(): %r = %r", _name, _value)
                _IssueLevelImpl.addname(_name, _value)

    def issuelevelerror(self):  # type: (...) -> typing.Optional[_AnyIssueLevelType]
        """
        Retrieves the issue level from and above which known issues should be considered as errors.

        :return: Error issue level if set, ``None`` otherwise.
        """
        if _FAST_PATH.exec_args and (_FAST_PATH.exec_args.issue_level_error is not None):
            self.debug("issuelevelerror() -> %r (from args)", _FAST_PATH.exec_args.issue_level_error)
            return _FAST_PATH.exec_args.issue_level_error
        else:
            _issue_level_error = _IssueLevelImpl.parse(_FAST_PATH.config_db.get(self.Key.ISSUE_LEVEL_ERROR, type=int)) \
                # type: typing.Optional[_AnyIssueLevelType]
            self.debug("issuelevelerror() -> %r (from config-db)", _issue_level_error)
            return _issue_level_error

    def issuelevelignored(self):  # type: (...) -> typing.Optional[_AnyIssueLevelType]
        """
        Retrieves the issue level from and under which known issues should be ignored.

        :return: Ignored issue level if set, ``None`` otherwise.
        """
        if _FAST_PATH.exec_args and (_FAST_PATH.exec_args.issue_level_ignored is not None):
            self.debug("issuelevelignored() -> %r (from args)", _FAST_PATH.exec_args.issue_level_ignored)
            return _FAST_PATH.exec_args.issue_level_ignored
        else:
            _issue_level_ignored = _IssueLevelImpl.parse(_FAST_PATH.config_db.get(self.Key.ISSUE_LEVEL_IGNORED, type=int)) \
                # type: typing.Optional[_AnyIssueLevelType]
            self.debug("issuelevelignored() -> %r (from config-db)", _issue_level_ignored)
            return _issue_level_ignored

    def _readstringlistfromconf(
            self,
            config_key,  # type: ScenarioConfig.Key
            allow_empty_strings=False,  # type: bool
    ):  # type: (...) -> typing.Sequence[typing.Tuple[str, _ConfigNodeType]]
        """
        Reads a string list from the configuration database.

        :param config_key:
            Configuration key for the string list.

            The configuration node pointed by ``config_key`` may be either a list of strings, or a comma-separated string.
        :param allow_empty_strings:
            ``False`` to ignore empty strings.

            ``False`` by default.
        :return:
            Strings with related configuration nodes.
        """
        _strings = []  # type: typing.List[str]
        _nodes = []  # type: typing.List[_ConfigNodeType]

        _node = _FAST_PATH.config_db.getnode(config_key)  # type: typing.Optional[_ConfigNodeType]
        if _node:
            _data = _node.data  # type: typing.Any
            if isinstance(_data, list):
                for _sub_key in _node.getsubkeys():  # type: str
                    _sub_node = _node.get(_sub_key)  # type: typing.Optional[_ConfigNodeType]
                    # `_node.get()` should always return a sub-node in this situation.
                    if not _sub_node:
                        raise RuntimeError("Internal error")

                    if isinstance(_sub_node.data, str):
                        if allow_empty_strings or _sub_node.data:
                            _strings.append(_sub_node.data)
                            _nodes.append(_sub_node)
                    else:
                        self.warning(_sub_node.errmsg(f"Invalid string {_sub_node.data!r}"))
            elif isinstance(_data, str):
                for _part in _data.split(","):  # type: str
                    _part = _part.strip()

                    if allow_empty_strings or _part:
                        _strings.append(_part)
                        _nodes.append(_node)
            else:
                self.warning(_node.errmsg(f"Invalid string list {_data!r}"))

        if len(_strings) != len(_nodes):
            raise RuntimeError("Internal error")
        return list(zip(_strings, _nodes))

    def _readpathlistfromconf(
            self,
            config_key,  # type: ScenarioConfig.Key
    ):  # type: (...) -> typing.Sequence[_PathType]
        """
        Reads a path list from the configuration database.

        :param config_key:
            Configuration key for the path list.

            The configuration node pointed by ``config_key`` may be either a list of strings, or a comma-separated string.

            Each string may describe either an absolute path,
            or a relative path from the source configuration file.
        :return:
            List of paths.
        :raise FileNotFoundError:
            In case of relative path not described in a configuration file.
        """
        _paths = []  # type: typing.List[_PathType]
        for _string, _node in self._readstringlistfromconf(config_key):  # type: str, _ConfigNodeType
            if _PathImpl.is_absolute(_string):
                _paths.append(_PathImpl(_string))
            elif _node.source_file:
                _paths.append(_PathImpl(_string, relative_to=_node.source_file.parent))
            else:
                raise FileNotFoundError(_node.errmsg(f"Invalid file path {_string!r}"))
        return _paths


#: Main instance of :class:`ScenarioConfig`.
#:
#: Also available as :attr:`._fastpath.FastPath.scenario_config`.
#: Please prefer the latter instead of using local imports of this module.
SCENARIO_CONFIG = ScenarioConfig()  # type: ScenarioConfig
