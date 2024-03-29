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

# `ConfigNode` used in method signatures.
from .confignode import ConfigNode
# `Console` used in method signatures.
from .console import Console
# `StrEnum` used for inheritance.
from .enumutils import StrEnum
if typing.TYPE_CHECKING:
    # `AnyIssueLevelType` used in method signatures.
    from .issuelevels import AnyIssueLevelType
# `Path` used in method signatures.
from .path import Path


class ScenarioConfig:
    """
    `scenario` configuration management.

    This class defines static methods that help reading `scenario` configurations:
    from the program arguments (see: :class:`.args.Args`),
    and the configuration database (see: :class:`.configdb.ConfigDatabase`).
    """

    class Key(StrEnum):
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
        Initializes the timezone cache information.
        """
        #: Timezone cache information.
        self.__timezone = None  # type: typing.Optional[str]

    def timezone(self):  # type: (...) -> typing.Optional[str]
        """
        Gives the timezone configuration, if set.

        :return:
            Timezone configuration if set, ``None`` otherwise.

            When not set, the local timezone is used.
        """
        from .configdb import CONFIG_DB

        if self.__timezone is None:
            # Set the cache member with an empty string if no configuration is set.
            self.__timezone = (CONFIG_DB.get(self.Key.TIMEZONE, type=str) or "").strip()
        # Convert empty string to `None`.
        return self.__timezone or None

    def invalidatetimezonecache(self):  # type: (...) -> None
        """
        Invalidates the timezone cache information.
        """
        self.__timezone = None

    def logdatetimeenabled(self):  # type: (...) -> bool
        """
        Determines whether the Log line should include a timestamp.

        Configurable through :const:`Key.LOG_DATETIME`.
        """
        from .configdb import CONFIG_DB

        return CONFIG_DB.get(self.Key.LOG_DATETIME, type=bool, default=True)

    def logconsoleenabled(self):  # type: (...) -> bool
        """
        Determines whether the log should be displayed in the console.

        Configurable through :const:`Key.LOG_CONSOLE`.
        """
        from .configdb import CONFIG_DB

        return CONFIG_DB.get(self.Key.LOG_CONSOLE, type=bool, default=True)

    def logoutpath(self):  # type: (...) -> typing.Optional[Path]
        """
        Determines whether the log lines should be written in a log file.

        :return: Output log file path if set, ``None`` indicates no file logging.

        Configurable through :const:`Key.LOG_FILE`.
        """
        from .configdb import CONFIG_DB

        _log_outpath = None  # type: typing.Optional[Path]
        _config = CONFIG_DB.get(self.Key.LOG_FILE, type=str)  # type: typing.Optional[str]
        if _config is not None:
            _log_outpath = Path(_config)
        return _log_outpath

    def logcolorenabled(self):  # type: (...) -> bool
        """
        Determines whether log colors should be used when displayed in the console.

        Configurable through :const:`Key.LOG_COLOR_ENABLED`.
        """
        from .configdb import CONFIG_DB

        return CONFIG_DB.get(self.Key.LOG_COLOR_ENABLED, type=bool, default=True)

    def logcolor(
            self,
            level,  # type: str
            default,  # type: Console.Color
    ):  # type: (...) -> Console.Color
        """
        Retrieves the expected log color for the given log level.

        :param level: Log level name.
        :param default: Default log color.
        :return: Log color configured, or default if not set.

        Configurable through :attr:`Key.LOG_COLOR`.
        """
        from .configdb import CONFIG_DB, ConfigNode

        _key = str(self.Key.LOG_COLOR) % level.lower()  # type: str
        _config_node = CONFIG_DB.getnode(_key)  # type: typing.Optional[ConfigNode]
        if _config_node:
            _color_number = _config_node.cast(type=int)  # type: int
            if _color_number is not None:
                try:
                    return Console.Color(_color_number)
                except ValueError:
                    self._warning(_config_node, f"Invalid color number {_color_number!r}")
        return default

    def debugclasses(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the debug classes configured.

        :return: List of debug classes.

        Adds debug classes defined by the program arguments (see :attr:`.args.Args.debug_classes`)
        plus those defined by the configurations (see :const:`Key.DEBUG_CLASSES`).
        """
        from .args import Args

        # Merge debug classes from...
        _debug_classes = []  # type: typing.List[str]
        # ...arguments,
        for _debug_class in Args.getinstance().debug_classes:  # type: str
            if _debug_class not in _debug_classes:
                _debug_classes.append(_debug_class)
        # ...and configuration database.
        self._readstringlistfromconf(self.Key.DEBUG_CLASSES, _debug_classes)
        return _debug_classes

    def expectedscenarioattributes(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the user scenario expected attributes.

        Configurable through :attr:`Key.EXPECTED_ATTRIBUTES`.
        """
        _attribute_names = []  # type: typing.List[str]
        self._readstringlistfromconf(self.Key.EXPECTED_ATTRIBUTES, _attribute_names)
        return _attribute_names

    def continueonerror(self):  # type: (...) -> bool
        """
        Determines whether the test should continue when a step ends in error.

        Configurable through :const:`Key.CONTINUE_ON_ERROR`.
        """
        from .configdb import CONFIG_DB

        return CONFIG_DB.get(self.Key.CONTINUE_ON_ERROR, type=bool, default=False)

    def delaybetweensteps(self):  # type: (...) -> float
        """
        Retrieves the expected delay between steps.

        Checks in configurations only (see :attr:`Key.DELAY_BETWEEN_STEPS`).
        """
        from .configdb import CONFIG_DB

        return CONFIG_DB.get(self.Key.DELAY_BETWEEN_STEPS, type=float, default=0.001)

    def runnerscriptpath(self):  # type: (...) -> Path
        """
        Gives the path of the scenario runner script path.

        Useful when executing campaigns.
        """
        from .configdb import CONFIG_DB

        _abspath = CONFIG_DB.get(self.Key.RUNNER_SCRIPT_PATH, type=str, default=Path(__file__).parents[2] / "bin" / "run-test.py")  # type: str
        return Path(_abspath)

    def scenariotimeout(self):  # type: (...) -> float
        """
        Retrieves the maximum time for a scenario execution.

        Useful when executing campaigns.

        Checks in configurations only (see :attr:`Key.SCENARIO_TIMEOUT`).
        """
        from .configdb import CONFIG_DB

        return CONFIG_DB.get(self.Key.SCENARIO_TIMEOUT, type=float, default=600.0)

    def resultsextrainfo(self):  # type: (...) -> typing.List[str]
        """
        Retrieves the list of scenario attributes to display for extra info when displaying test results.

        :return: List of scenario attribute names.

        Applicable when displaying campaign results
        or the result of several tests executed in a single command line.
        """
        from .args import Args
        from .campaignargs import CampaignArgs
        from .scenarioargs import ScenarioArgs

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
        return _attribute_names

    def loadissuelevelnames(self):  # type: (...) -> None
        """
        Loads the issue level names configured through configuration files.
        """
        from .configdb import CONFIG_DB
        from .issuelevels import IssueLevel

        _root_node = CONFIG_DB.getnode(self.Key.ISSUE_LEVEL_NAMES)  # type: typing.Optional[ConfigNode]
        if _root_node:
            for _name in _root_node.getsubkeys():  # type: str
                # Retrieve the `int` value configured with the issue level name.
                _subnode = _root_node.get(_name)  # type: typing.Optional[ConfigNode]
                assert _subnode, "Internal error"
                try:
                    _value = _subnode.cast(int)  # type: int
                except ValueError as _err:
                    self._warning(_subnode, f"Not an integer value {_subnode.data!r}, issue level name ignored")
                    continue

                # Check value consistency when the issue level name is already known.
                if _name in IssueLevel.getnamed():
                    if _value != IssueLevel.parse(_name):
                        self._warning(_subnode, f"Name already set {IssueLevel.getdesc(IssueLevel.parse(_name))}, issue level name {_name}={_value!r} ignored")
                    continue

                # Save the association between the new issue level name and value.
                IssueLevel.addname(_name, _value)

    def issuelevelerror(self):  # type: (...) -> typing.Optional[AnyIssueLevelType]
        """
        Retrieves the issue level from and above which known issues should be considered as errors.

        :return: Error issue level if set, ``None`` otherwise.
        """
        from .args import Args
        from .configdb import CONFIG_DB
        from .issuelevels import IssueLevel
        if typing.TYPE_CHECKING:
            from .issuelevels import AnyIssueLevelType
        from .scenarioargs import CommonExecArgs

        _args = Args.getinstance()  # type: Args
        if isinstance(_args, CommonExecArgs):
            if _args.issue_level_error is not None:
                return _args.issue_level_error

        return IssueLevel.parse(CONFIG_DB.get(self.Key.ISSUE_LEVEL_ERROR, type=int))

    def issuelevelignored(self):  # type: (...) -> typing.Optional[AnyIssueLevelType]
        """
        Retrieves the issue level from and under which known issues should be ignored.

        :return: Ignored issue level if set, ``None`` otherwise.
        """
        from .args import Args
        from .configdb import CONFIG_DB
        from .issuelevels import IssueLevel
        if typing.TYPE_CHECKING:
            from .issuelevels import AnyIssueLevelType
        from .scenarioargs import CommonExecArgs

        _args = Args.getinstance()  # type: Args
        if isinstance(_args, CommonExecArgs):
            if _args.issue_level_ignored is not None:
                return _args.issue_level_ignored

        return IssueLevel.parse(CONFIG_DB.get(self.Key.ISSUE_LEVEL_IGNORED, type=int))

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
        from .configdb import CONFIG_DB

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
                self._warning(_conf_node, f"Invalid type {type(_data)}")

    def _warning(
            self,
            node,  # type: ConfigNode
            msg,  # type: str
    ):  # type: (...) -> None
        """
        Logs a warning message for the given configuration node.

        :param node: Configuration node related to the warning.
        :param msg: Warning message.
        """
        from .configdb import CONFIG_DB

        CONFIG_DB.warning(node.errmsg(msg))


__doc__ += """
.. py:attribute:: ScenarioConfigKey

    Shortcut to the :class:`ScenarioConfig.Key` enum in order to make it possible to import it without the :class:`ScenarioConfig` class.
"""
ScenarioConfigKey = ScenarioConfig.Key


__doc__ += """
.. py:attribute:: SCENARIO_CONFIG

    Main instance of :class:`ScenarioConfig`.
"""
SCENARIO_CONFIG = ScenarioConfig()  # type: ScenarioConfig
