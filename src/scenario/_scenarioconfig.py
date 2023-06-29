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
    from ._enumutils import StrEnum as _StrEnumImpl  # `StrEnum` used for inheritance.
    from ._logger import Logger as _LoggerImpl  # `Logger` used for inheritance.
if typing.TYPE_CHECKING:
    from ._console import Console as _ConsoleType
    from ._issuelevels import AnyIssueLevelType as _AnyIssueLevelType
    from ._path import Path as _PathType


class ScenarioConfig(_LoggerImpl):
    """
    `scenario` configuration management.

    This class defines static methods that help reading `scenario` configurations:
    from the program arguments (see: :class:`._args.Args`),
    and the configuration database (see: :class:`._configdb.ConfigDatabase`).
    """

    class Key(_StrEnumImpl):
        """
        `scenario` configuration keys.
        """

        # Time & logging.

        #: Should a specific timezone be used? String value. Default is the local timezone.
        TIMEZONE = "scenario.timezone"
        #: Should the log lines include a timestamp? Boolean value.
        LOG_DATETIME = "scenario.log_date_time"
        #: Should the log lines be displayed in the console? Boolean value.
        LOG_CONSOLE = "scenario.log_console"
        #: Should the log lines be colored? Boolean value.
        LOG_COLOR_ENABLED = "scenario.log_color"
        #: Log color per log level. Integer value.
        LOG_COLOR = "scenario.log_%s_color"
        #: Should the log lines be written in a log file? File path string.
        LOG_FILE = "scenario.log_file"
        #: Which debug classes to display? List of strings, or comma-separated string.
        DEBUG_CLASSES = "scenario.debug_classes"

        # Test execution & results.

        #: Expected scenario attributes. List of strings, or comma-separated string.
        EXPECTED_ATTRIBUTES = "scenario.expected_attributes"
        #: Should the scenario continue on error? Boolean value.
        CONTINUE_ON_ERROR = "scenario.continue_on_error"
        #: Should we wait between two step executions? Float value.
        DELAY_BETWEEN_STEPS = "scenario.delay_between_steps"
        #: Runner script path. Default is 'bin/run-test.py'.
        RUNNER_SCRIPT_PATH = "scenario.runner_script_path"
        #: Maximum time for a scenario execution. Useful when executing campaigns. Float value.
        SCENARIO_TIMEOUT = "scenario.scenario_timeout"
        #: Scenario attributes to display for extra info when displaying scenario results,
        #: after a campaign execution, or when executing several tests in a single command line.
        #: List of strings, or comma-separated string.
        RESULTS_EXTRA_INFO = "scenario.results_extra_info"

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
        from ._debugclasses import DebugClass

        _LoggerImpl.__init__(self, DebugClass.SCENARIO_CONFIG)

        #: Timezone cache information.
        self.__timezone = None  # type: typing.Optional[str]

    def timezone(self):  # type: (...) -> typing.Optional[str]
        """
        Gives the timezone configuration, if set.

        :return:
            Timezone configuration if set, ``None`` otherwise.

            When not set, the local timezone is used.
        """
        from ._configdb import CONFIG_DB

        if self.__timezone is None:
            # Set the cache member with an empty string if no configuration is set.
            self.__timezone = (CONFIG_DB.get(self.Key.TIMEZONE, type=str) or "").strip()
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
        from ._configdb import CONFIG_DB

        _log_datetime_enabled = CONFIG_DB.get(self.Key.LOG_DATETIME, type=bool, default=True)  # type: bool
        # Don't debug `logdatetimeenabled()`, otherwise it may cause infinite recursions when logging.
        # self.debug("logdatetimeenabled() -> %r", _log_datetime_enabled)
        return _log_datetime_enabled

    def logconsoleenabled(self):  # type: (...) -> bool
        """
        Determines whether the log should be displayed in the console.

        Configurable through :const:`Key.LOG_CONSOLE`.
        """
        from ._configdb import CONFIG_DB

        _log_console_enabled = CONFIG_DB.get(self.Key.LOG_CONSOLE, type=bool, default=True)  # type: bool
        # Don't debug `logconsoleenabled()`, otherwise it may cause infinite recursions when logging.
        # self.debug("logconsoleenabled() -> %r", _log_console_enabled)
        return _log_console_enabled

    def logoutpath(self):  # type: (...) -> typing.Optional[_PathType]
        """
        Determines whether the log lines should be written in a log file.

        :return: Output log file path if set, ``None`` indicates no file logging.

        Configurable through :const:`Key.LOG_FILE`.
        """
        from ._configdb import CONFIG_DB
        from ._path import Path

        _log_outpath = None  # type: typing.Optional[Path]
        _config = CONFIG_DB.get(self.Key.LOG_FILE, type=str)  # type: typing.Optional[str]
        if _config is not None:
            _log_outpath = Path(_config)

        # Don't debug `logoutpath()`, otherwise it may cause infinite recursions when logging (tbc).
        # self.debug("logoutpath() -> %r", _log_outpath)
        return _log_outpath

    def logcolorenabled(self):  # type: (...) -> bool
        """
        Determines whether log colors should be used when displayed in the console.

        Configurable through :const:`Key.LOG_COLOR_ENABLED`.
        """
        from ._configdb import CONFIG_DB

        _log_color_enabled = CONFIG_DB.get(self.Key.LOG_COLOR_ENABLED, type=bool, default=True)  # type: bool
        # Don't debug `logcolorenabled()`, otherwise it may cause infinite recursions when logging.
        # self.debug("logcolorenabled() -> %r", _log_color_enabled)
        return _log_color_enabled

    def logcolor(
            self,
            level,  # type: str
            default,  # type: _ConsoleType.Color
    ):  # type: (...) -> _ConsoleType.Color
        """
        Retrieves the expected log color for the given log level.

        :param level: Log level name.
        :param default: Default log color.
        :return: Log color configured, or default if not set.

        Configurable through :attr:`Key.LOG_COLOR`.
        """
        from ._configdb import CONFIG_DB
        from ._confignode import ConfigNode
        from ._console import Console

        _key = str(self.Key.LOG_COLOR) % level.lower()  # type: str
        _config_node = CONFIG_DB.getnode(_key)  # type: typing.Optional[ConfigNode]
        if _config_node:
            _color_number = _config_node.cast(type=int)  # type: int
            if _color_number is not None:
                try:
                    # Don't debug `logcolor()`, otherwise it may cause infinite recursions when logging.
                    # self.debug("logcolor(level=%r, default=%r) -> %r", level, default, Console.Color(_color_number))
                    return Console.Color(_color_number)
                except ValueError:
                    self.warning(_config_node.errmsg(f"Invalid color number {_color_number!r}"))
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
        from ._args import Args

        # Merge debug classes from...
        _debug_classes = []  # type: typing.List[str]
        # ...arguments,
        for _debug_class in Args.getinstance().debug_classes:  # type: str
            if _debug_class not in _debug_classes:
                _debug_classes.append(_debug_class)
        # ...and configuration database.
        self._readstringlistfromconf(self.Key.DEBUG_CLASSES, _debug_classes)
        # Don't debug `debugclasses()`, otherwise it may cause infinite recursions when logging.
        # self.debug("debugclasses() -> %r", _debug_classes)
        return _debug_classes

    def expectedscenarioattributes(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the user scenario expected attributes.

        Configurable through :attr:`Key.EXPECTED_ATTRIBUTES`.
        """
        _attribute_names = []  # type: typing.List[str]
        self._readstringlistfromconf(self.Key.EXPECTED_ATTRIBUTES, _attribute_names)
        self.debug("expectedscenarioattributes() -> %r", _attribute_names)
        return _attribute_names

    def continueonerror(self):  # type: (...) -> bool
        """
        Determines whether the test should continue when a step ends in error.

        Configurable through :const:`Key.CONTINUE_ON_ERROR`.
        """
        from ._configdb import CONFIG_DB

        _continue_on_error = CONFIG_DB.get(self.Key.CONTINUE_ON_ERROR, type=bool, default=False)  # type: bool
        self.debug("continueonerror() -> %r", _continue_on_error)
        return _continue_on_error

    def delaybetweensteps(self):  # type: (...) -> float
        """
        Retrieves the expected delay between steps.

        Checks in configurations only (see :attr:`Key.DELAY_BETWEEN_STEPS`).
        """
        from ._configdb import CONFIG_DB

        _delay_between_steps = CONFIG_DB.get(self.Key.DELAY_BETWEEN_STEPS, type=float, default=0.001)  # type: float
        self.debug("delaybetweensteps() -> %r", _delay_between_steps)
        return _delay_between_steps

    def runnerscriptpath(self):  # type: (...) -> _PathType
        """
        Gives the path of the scenario runner script path.

        Useful when executing campaigns.
        """
        from ._configdb import CONFIG_DB
        from ._path import Path

        _abspath = CONFIG_DB.get(self.Key.RUNNER_SCRIPT_PATH, type=str, default=Path(__file__).parents[2] / "bin" / "run-test.py")  # type: str
        self.debug("runnerscriptpath() -> %r", Path(_abspath))
        return Path(_abspath)

    def scenariotimeout(self):  # type: (...) -> float
        """
        Retrieves the maximum time for a scenario execution.

        Useful when executing campaigns.

        Checks in configurations only (see :attr:`Key.SCENARIO_TIMEOUT`).
        """
        from ._configdb import CONFIG_DB

        _scenario_timeout = CONFIG_DB.get(self.Key.SCENARIO_TIMEOUT, type=float, default=600.0)  # type: float
        self.debug("scenariotimeout() -> %r", _scenario_timeout)
        return _scenario_timeout

    def resultsextrainfo(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the list of scenario attributes to display for extra info when displaying test results.

        :return: List of scenario attribute names.

        Applicable when displaying campaign results
        or the result of several tests executed in a single command line.
        """
        from ._args import Args
        from ._campaignargs import CampaignArgs
        from ._scenarioargs import ScenarioArgs

        # Merge attribute names from...
        _attribute_names = []  # type: typing.List[str]
        # ...arguments,
        _args = Args.getinstance()  # type: Args
        if isinstance(_args, (ScenarioArgs, CampaignArgs)):
            for _attribute_name in _args.extra_info:  # type: str
                if _attribute_name not in _attribute_names:
                    _attribute_names.append(_attribute_name)
        # ...and configuration database.
        self._readstringlistfromconf(self.Key.RESULTS_EXTRA_INFO, _attribute_names)
        self.debug("resultsextrainfo() -> %r", _attribute_names)
        return _attribute_names

    def loadissuelevelnames(self):  # type: (...) -> None
        """
        Loads the issue level names configured through configuration files.
        """
        from ._configdb import CONFIG_DB
        from ._confignode import ConfigNode
        from ._issuelevels import IssueLevel

        _root_node = CONFIG_DB.getnode(self.Key.ISSUE_LEVEL_NAMES)  # type: typing.Optional[ConfigNode]
        if _root_node:
            for _name in _root_node.getsubkeys():  # type: str
                # Retrieve the `int` value configured with the issue level name.
                _subnode = _root_node.get(_name)  # type: typing.Optional[ConfigNode]
                assert _subnode, "Internal error"
                try:
                    _value = _subnode.cast(int)  # type: int
                except ValueError as _err:
                    self.warning(_subnode.errmsg(f"Not an integer value {_subnode.data!r}, issue level name ignored"))
                    continue

                # Check value consistency when the issue level name is already known.
                if _name in IssueLevel.getnamed():
                    if _value != IssueLevel.parse(_name):
                        self.warning(_subnode.errmsg(
                            f"Name already set {IssueLevel.getdesc(IssueLevel.parse(_name))}, issue level name {_name}={_value!r} ignored"
                        ))
                    continue

                # Save the association between the new issue level name and value.
                self.debug("loadissuelevelnames(): %r = %r", _name, _value)
                IssueLevel.addname(_name, _value)

    def issuelevelerror(self):  # type: (...) -> typing.Optional[_AnyIssueLevelType]
        """
        Retrieves the issue level from and above which known issues should be considered as errors.

        :return: Error issue level if set, ``None`` otherwise.
        """
        from ._args import Args
        from ._configdb import CONFIG_DB
        from ._issuelevels import IssueLevel
        from ._scenarioargs import CommonExecArgs

        _args = Args.getinstance()  # type: Args
        if isinstance(_args, CommonExecArgs):
            if _args.issue_level_error is not None:
                self.debug("issuelevelerror() -> %r (from args)", _args.issue_level_error)
                return _args.issue_level_error

        _issue_level_error = IssueLevel.parse(CONFIG_DB.get(self.Key.ISSUE_LEVEL_ERROR, type=int))  # type: typing.Optional[_AnyIssueLevelType]
        self.debug("issuelevelerror() -> %r (from config-db)", _issue_level_error)
        return _issue_level_error

    def issuelevelignored(self):  # type: (...) -> typing.Optional[_AnyIssueLevelType]
        """
        Retrieves the issue level from and under which known issues should be ignored.

        :return: Ignored issue level if set, ``None`` otherwise.
        """
        from ._args import Args
        from ._configdb import CONFIG_DB
        from ._issuelevels import IssueLevel
        from ._scenarioargs import CommonExecArgs

        _args = Args.getinstance()  # type: Args
        if isinstance(_args, CommonExecArgs):
            if _args.issue_level_ignored is not None:
                self.debug("issuelevelignored() -> %r (from args)", _args.issue_level_ignored)
                return _args.issue_level_ignored

        _issue_level_ignored = IssueLevel.parse(CONFIG_DB.get(self.Key.ISSUE_LEVEL_IGNORED, type=int))  # type: typing.Optional[_AnyIssueLevelType]
        self.debug("issuelevelignored() -> %r (from config-db)", _issue_level_ignored)
        return _issue_level_ignored

    def _readstringlistfromconf(
            self,
            config_key,  # type: ScenarioConfig.Key
            outlist,  # type: typing.List[str]
    ):  # type: (...) -> None
        """
        Reads a string list from the configuration database, and feeds an output list.

        :param config_key:
            Configuration key for the string list.

            The configuration node pointed by ``config_key`` may be either a list of strings, or a comma-separated string.
        :param outlist:
            Output string list to feed.

            Values are prevented in case of duplicates.
        """
        from ._configdb import CONFIG_DB
        from ._confignode import ConfigNode

        _conf_node = CONFIG_DB.getnode(config_key)  # type: typing.Optional[ConfigNode]
        if _conf_node:
            _data = _conf_node.data  # type: typing.Any
            if isinstance(_data, list):
                for _item in _data:  # type: typing.Any
                    if _item and isinstance(_item, str) and (_item not in outlist):
                        outlist.append(_item)
            elif isinstance(_data, str):
                for _part in _data.split(","):  # type: str
                    _part = _part.strip()
                    if _part and (_part not in outlist):
                        outlist.append(_part)
            else:
                self.warning(_conf_node.errmsg(f"Invalid type {type(_data)}"))


#: Main instance of :class:`ScenarioConfig`.
SCENARIO_CONFIG = ScenarioConfig()  # type: ScenarioConfig
